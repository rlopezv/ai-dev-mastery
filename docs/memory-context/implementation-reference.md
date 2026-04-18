---
id: "memory-context-implementation-reference"
title: "Memory and Context Management — Implementation Reference"
type: "implementation-reference"
step: "memory-context"
path: "docs/memory-context/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "conversation history"
  - "context management"
  - "external memory"
  - "token budget"
  - "memory retrieval"

prerequisites:
  - "docs/memory-context/architecture.md"

next:
  - "docs/memory-context/validation.md"

related:
  - "docs/memory-context/conversation-history.md"
  - "docs/memory-context/context-management.md"
  - "docs/memory-context/external-memory.md"
  - "docs/rag/implementation-reference.md"

implementation_refs:
  - "labs/memory-context/lab-conversation-history"
  - "labs/memory-context/lab-context-management"
  - "labs/memory-context/lab-external-memory"
  - "labs/memory-context/lab-integration"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains the implementation patterns for conversation history management, context budget enforcement, and external memory across the memory-context labs."
---

# Memory and Context Management — Implementation Reference

## Navigation

[Docs](../README.md) / [Memory and Context Management](README.md) / Memory and Context Management — Implementation Reference

---

## 1. Implementation Overview

The memory-context module is implemented across four labs that each isolate a distinct
component: history accumulation, context management strategies, external memory write and
retrieval, and full system integration. A shared module (`labs/memory-context/shared/`)
provides the LLM client, token counter, embedding client, and ChromaDB wrapper used by
all labs.

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| History accumulation | Append user + assistant messages; pass full list on every call | All multi-turn conversations |
| Budget ceiling | Count tokens before each call; enforce maximum before appending | Any history that may exceed context window |
| Sliding window | Keep last N turn pairs; drop older ones | Short conversations where recency suffices |
| Summarization compression | Replace oldest N turns with a model-generated summary | Long conversations where early context matters |
| Memory retrieval injection | Query external store with current message; inject results into system context | Cross-session recall, personalization |
| Async memory write | Extract and write memory entry after response is returned | Production systems where latency matters |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| History Manager | `list[dict]` maintained in application scope; `shared/history.py` |
| Token Budget Calculator | `count_tokens()` in `shared/config.py` |
| Context Management Strategy | `apply_sliding_window()`, `compress_history()` in `shared/context.py` |
| Memory Retriever | `MemoryStore.search()` in `shared/memory.py` |
| Memory Writer | `MemoryStore.add()`, `MemoryStore.upsert()` in `shared/memory.py` |
| Context Assembler | `assemble_messages()` in `shared/context.py` |
| LLM Client | `build_client()` in `shared/config.py` |

---

## 4. Data Structures and Interfaces

**History list.** A Python list of `dict` objects following the chat completion message
format. Role must alternate strictly between `user` and `assistant`.

```python
# Orientative — see labs/memory-context/lab-conversation-history/main.py
history: list[dict] = []

# Append pattern
history.append({"role": "user", "content": user_message})
history.append({"role": "assistant", "content": assistant_reply})
```

**Token budget configuration.**

```python
# Orientative — see labs/memory-context/shared/config.py
CONTEXT_WINDOW: int           # model context window size in tokens
SYSTEM_PROMPT_TOKENS: int     # pre-counted system prompt token cost
OUTPUT_RESERVATION: int       # reserved tokens for model output
SAFETY_MARGIN: int            # buffer for token count approximation error
HISTORY_BUDGET: int = (
    CONTEXT_WINDOW - SYSTEM_PROMPT_TOKENS - OUTPUT_RESERVATION - SAFETY_MARGIN
)
COMPRESSION_THRESHOLD: float = 0.80  # compress at 80% of HISTORY_BUDGET
```

**Memory store entry.**

```python
# Orientative — see labs/memory-context/shared/memory.py
class MemoryEntry(TypedDict):
    id: str              # unique entry ID (UUID for episodes, entity_id for semantic)
    text: str            # embedded and stored text
    metadata: dict       # type ("episode" | "semantic"), session_id, timestamp, entity
```

**Context assembler output.**

```python
# Orientative — see labs/memory-context/shared/context.py
def assemble_messages(
    system_prompt: str,
    memory_entries: list[MemoryEntry],
    history: list[dict],
    user_message: str,
) -> list[dict]:
    """
    Build the messages list for the API call.
    Order: system → memory context → history → user message.
    """
```

---

## 5. Design Decisions

**`shared/` is the single source of token counting.** All labs import `count_tokens()`
from `shared/config.py`. Duplicating this function across labs would cause inconsistencies
in budget calculations. The shared implementation uses tiktoken with a configurable
model encoding.

**Compression threshold is percentage-based, not absolute.** Setting the threshold at 80%
of the history budget rather than at the budget itself leaves a window for the compression
call to execute without causing the next API call to fail. An absolute threshold at the
budget limit would allow the compression call itself to push total tokens over the limit
if the summary is long.

**Memory entries are embedded at write time, not at retrieval time.** Embedding at write
time means each entry is embedded once. Embedding at retrieval time would re-embed every
query but require no storage of vectors — a valid alternative for very small stores but
impractical at scale.

**The context assembler allocates tokens in priority order.** System prompt tokens are
fixed and always included. Memory context is injected next, up to a secondary budget
(`memory_budget = HISTORY_BUDGET * 0.3`). Remaining space is allocated to history. This
prevents memory injection from consuming the entire history budget.

---

## 6. External Dependencies

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| Ollama | LLM inference and embeddings | `light` |
| ChromaDB | Vector store for external memory | `full` |

Labs 1–3 (`lab-memory-types`, `lab-conversation-history`, `lab-context-management`) use
only the `light` profile. `lab-external-memory` and `lab-integration` require `full`.

---

## 7. Mapping to Labs

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| History accumulation + token counting | `lab-conversation-history` | History grows by 2 messages per turn; budget enforcement prevents API errors |
| Sliding window | `lab-context-management` | Recent turns preserved; early context lost |
| Summarization compression | `lab-context-management` | Early context preserved in compressed form; 1 additional API call per event |
| Memory write (episodic) | `lab-external-memory` | Episode stored and retrievable in next session |
| Memory write (semantic / upsert) | `lab-external-memory` | Fact update propagates to retrieval |
| Memory retrieval injection | `lab-external-memory` | Retrieved entries injected as system context |
| Full system assembly | `lab-integration` | All components compose without budget violation |

---

## 8. Trade-offs and Constraints

**tiktoken accuracy for open-weight models.** tiktoken is accurate for GPT-family models.
For Ollama-served models (Mistral, LLaMA), token counts may differ by 2–5%. The safety
margin in `HISTORY_BUDGET` absorbs this error. Reducing the safety margin below 5% risks
occasional budget overflows under high-token-variance messages.

**ChromaDB in-process vs server mode.** The labs use ChromaDB in in-process mode
(`chromadb.Client()`), which stores data in memory and does not persist across process
restarts. `lab-external-memory` uses the persistent client (`chromadb.PersistentClient()`)
to demonstrate cross-session recall. The architecture document covers the production
alternative: a ChromaDB server accessed via HTTP.

**Summarization model vs generation model.** The compression step can use a smaller,
faster model for summarization and a larger model for generation. The labs use the same
Ollama model for both. In production systems, separating the two reduces summarization
cost and latency.

---

## 9. Failure Modes

**Missing role alternation.** If a bug causes two consecutive `user` messages to be
appended (e.g., after a failed compression that drops one message), some providers return
a 400 error with "invalid message format." The history manager must validate alternation
before every API call, not only at append time.

**Memory store cold start.** `MemoryStore.search()` returns an empty list when the store
contains no entries. The context assembler must handle empty retrieval results without
injecting a blank memory context block, which can confuse the model into fabricating
recalled facts.

**Budget undercount under nested tool calls.** If tool-use messages (covered in
`structured-outputs`) are interleaved with conversation messages, `count_tokens()` must
account for tool call and tool result message overhead. The shared counter does not include
this overhead by default; labs that combine tool use with memory management must add it.

---

## 10. Summary

The memory-context implementation centers on three shared utilities: a token counter that
drives budget enforcement, a context management module that implements truncation and
summarization strategies, and a memory store wrapper that provides embeddings-backed
episodic and semantic storage. Labs are isolated by component: history, context management,
external memory, and integration. The shared module is the coordination point — consistent
token counting and a single context assembler prevent the budget violations and injection
ordering errors that arise when each lab manages these independently.
