---
id: "memory-context-architecture"
title: "Memory and Context Management — Architecture"
type: "architecture"
step: "memory-context"
path: "docs/memory-context/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "memory types"
  - "conversation history"
  - "context management"
  - "external memory"
  - "token budget"

prerequisites:
  - "docs/memory-context/README.md"
  - "docs/memory-context/memory-types.md"
  - "docs/memory-context/conversation-history.md"
  - "docs/memory-context/context-management.md"
  - "docs/memory-context/external-memory.md"

next:
  - "docs/memory-context/implementation-reference.md"

related:
  - "docs/rag/architecture.md"
  - "docs/llm-fundamentals/architecture.md"

implementation_refs:
  - "labs/memory-context/lab-integration"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the runtime architecture of a memory-aware LLM application, showing how the history manager, token budget calculator, context management strategy, and optional external memory store compose into a single request-response cycle."
---

## 1. System Overview

A memory-aware LLM application wraps the standard stateless API call with a stateful layer
that assembles, manages, and persists conversation context. The core problem it solves is
maintaining coherent multi-turn behavior over a stateless API while keeping the context
window within budget across conversations of arbitrary length.

The system handles two distinct time horizons: within a session (history accumulation and
budget management) and across sessions (external memory write and retrieval).

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| History Manager | State | Maintains the ordered list of prior turns; enforces role alternation |
| Token Budget Calculator | Constraint | Counts tokens in the current history; signals when the budget threshold is reached |
| Context Management Strategy | Policy | Decides how to reduce history when the budget is exceeded (truncation, sliding window, summarization) |
| Memory Retriever | Recall | Queries the external store for entries relevant to the current query |
| Memory Writer | Persistence | Extracts and stores memory entries after each turn |
| Context Assembler | Composition | Combines system prompt, retrieved memory, managed history, and user message into the final prompt |
| LLM Client | Execution | Calls the model API with the assembled context |

---

## 3. Component Interactions

The History Manager is the source of truth for within-session state. It owns the message
list and delegates to the Token Budget Calculator before each call to determine whether the
Context Management Strategy must run.

The Context Management Strategy modifies the history list in-place: it either truncates
messages or replaces old turns with a summarization call result. The resulting list is
passed to the Context Assembler.

The Memory Retriever runs at the start of each turn, querying the external store with the
current user message. Its output — zero or more retrieved entries — is passed to the Context
Assembler alongside the history.

The Context Assembler is stateless. It takes all inputs, applies token allocation priorities
(system prompt first, retrieved memory second, history third), and produces the final
`messages` list for the API call.

The Memory Writer runs after the model responds. It calls the model to extract a memory
entry from the completed turn and writes it to the external store asynchronously.

---

## 4. Data Flow

```text
User message
    │
    ▼
Memory Retriever ──────────────► External Store (ChromaDB)
    │ retrieved entries
    ▼
Token Budget Calculator ◄──── History Manager (message list)
    │ budget status
    ▼
Context Management Strategy  (runs only if budget exceeded)
    │ managed history
    ▼
Context Assembler
    ├── system prompt
    ├── retrieved memory entries
    ├── managed history
    └── current user message
    │
    ▼
LLM Client ──────────────────► Model API (Ollama / OpenAI / Anthropic)
    │ assistant reply
    ▼
History Manager ◄──────────── append (user + assistant)
    │
    ▼
Memory Writer (async) ────────► External Store (write episode or semantic fact)
    │
    ▼
Response returned to user
```

---

## 5. Execution Flow

**Turn start:**
1. Receive user message
2. Memory Retriever queries external store with user message as query (top-k = 3)
3. Token Budget Calculator counts current history tokens

**Context assembly:**
4. If history tokens > budget threshold: Context Management Strategy runs
5. Context Assembler builds `messages` list:
   - System prompt (fixed)
   - Retrieved memory block (if entries found)
   - Managed history
   - Current user message

**Inference:**
6. LLM Client calls model API
7. Assistant reply received

**Post-turn:**
8. History Manager appends user + assistant messages
9. Memory Writer calls model to extract memory entry (async)
10. If entry extracted: write to external store

**Compression event (within step 4):**
- Summarization strategy: call model with oldest N turns → replace with summary → recount tokens
- Sliding window: drop oldest pairs until within budget

---

## 6. Integration Points

| Integration | Direction | Protocol |
|-------------|-----------|----------|
| Ollama (LLM inference) | Outbound | OpenAI-compatible REST API |
| Ollama (embeddings) | Outbound | `/v1/embeddings` endpoint |
| ChromaDB (vector store) | Read/Write | Python client (`chromadb`) |
| Application (user interface) | Inbound | Function call or HTTP endpoint |

The architecture is provider-agnostic at the LLM level: swapping Ollama for OpenAI or
Anthropic requires only a client configuration change. ChromaDB is used for both episodic
and semantic memory; in production systems these may be split into separate collections or
separate stores.

---

## 7. Trade-offs and Design Decisions

**Async memory write vs synchronous.** Writing memory after the response is sent reduces
per-turn latency by 200–600ms but means a new entry is not available if the user sends
a follow-up immediately. Synchronous write guarantees consistency at the cost of latency.
The default in this module is async; synchronous is available as a configuration option in
`shared/config.py`.

**Single context assembler vs distributed assembly.** Assembling the full prompt in one
component makes token allocation explicit and auditable. Distributing assembly across
components (each one appending its own content) makes token budget management implicit
and harder to enforce. The single assembler is the canonical design.

**Summarization strategy vs sliding window.** Summarization preserves early context at the
cost of one additional API call per compression event. Sliding window is zero-cost but
loses early context permanently. The default is a hybrid: sliding window for short
conversations (under 20 turns), summarization-triggered at 80% of budget for longer ones.

**ChromaDB for both episodic and semantic memory.** Using one store simplifies the
infrastructure. The trade-off is that episodic and semantic entries share the retrieval
pool. A metadata filter on `type` separates them at query time.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| In-context vs external memory | `lab-memory-types` |
| History Manager + Token Budget Calculator | `lab-conversation-history` |
| Context Management Strategy (all variants) | `lab-context-management` |
| Memory Retriever + Memory Writer | `lab-external-memory` |
| Full system composition | `lab-integration` |

---

## 9. Limitations and Boundaries

**The architecture does not cover agent-level memory.** Agents that plan across multiple
steps, track tool-use state, or maintain scratchpads between reasoning cycles require
additional memory structures beyond history and external store. Those patterns are covered
in `ai-agents`.

**Retrieval accuracy is not guaranteed.** The Memory Retriever uses semantic similarity,
which can miss relevant entries if the query phrasing differs significantly from the stored
entry text. Recall is a function of embedding model quality and entry text quality, not a
property of the architecture.

**The external store requires infrastructure.** ChromaDB requires the `full` infrastructure
profile (`docker-compose --profile full`). Applications that cannot run ChromaDB must
implement external memory with an alternative store (PostgreSQL with pgvector, Redis with
vector search) or omit cross-session recall.

---

## 10. Summary

A memory-aware LLM application adds four components to the standard API call: a History
Manager that maintains the message list, a Token Budget Calculator that signals when the
list must be reduced, a Context Management Strategy that performs the reduction, and a
Memory Retriever and Writer that provide cross-session recall via a vector store. The
Context Assembler combines all inputs into the final prompt. Data flows from user message
through retrieval and assembly to the model, then back through history append and
asynchronous memory write. The key architectural decision is the separation between
within-session management (in-context, zero latency) and cross-session recall (external
store, retrieval latency).
