---
id: "memory-context-labs-readme"
title: "Memory and Context Management — Labs"
type: "lab-readme"
step: "memory-context"
path: "labs/memory-context/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "conversation history"
  - "token budget"
  - "context management"
  - "external memory"
  - "episodic memory"
  - "semantic memory"

prerequisites:
  - "docs/memory-context/README.md"
  - "docs/rag/embeddings-and-vector-search.md"

next:
  - "labs/ai-agents/README.md"

related:
  - "docs/memory-context/architecture.md"
  - "docs/memory-context/implementation-reference.md"

implementation_refs:
  - "labs/memory-context/lab-memory-types"
  - "labs/memory-context/lab-conversation-history"
  - "labs/memory-context/lab-context-management"
  - "labs/memory-context/lab-external-memory"
  - "labs/memory-context/lab-integration"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Guides the implementation of memory-aware LLM applications across five labs covering in-context observation, history management, context management strategies, external memory, and full system integration."
---

# Memory and Context Management — Labs

## Navigation

[Labs](../README.md) / Memory and Context Management — Labs

---


## 1. Overview

These labs implement the components of a memory-aware LLM application: from a token-bounded
history manager to cross-session recall using a local vector store. Each lab isolates one
architectural component, with the final integration lab assembling all components into a
working conversational application.

**What these labs cover:**
- Observing the behavioral difference between in-context and external memory
- Building a conversation loop with explicit token tracking and budget enforcement
- Implementing and comparing three context management strategies
- Writing and retrieving conversation episodes and semantic facts across sessions
- Composing all components into a memory-aware application

**What these labs do not cover:**
- Agent-level memory and planning state (covered in `ai-agents`)
- RAG over external document corpora (covered in `rag`)

---

## 2. Lab Inventory

| Lab | Description | Type | Decision |
|-----|-------------|------|----------|
| `lab-memory-types` | Observe in-context vs external memory behavior across a long conversation | observation | required |
| `lab-conversation-history` | Build a token-bounded multi-turn chat loop with explicit budget tracking | implementation | required |
| `lab-context-management` | Implement truncation, sliding window, and summarization strategies; measure recall accuracy | implementation | required |
| `lab-external-memory` | Write and retrieve conversation episodes and semantic facts across separate sessions | implementation | optional |
| `lab-integration` | Assemble all components into a memory-aware conversational application | module-integration | required |

---

## 3. Execution Model

All labs run as Python scripts via `python main.py` from the lab directory. No web server
is started — the labs interact with Ollama directly via the OpenAI-compatible API.

**Infrastructure required:**

| Lab | Ollama | ChromaDB |
|-----|--------|----------|
| `lab-memory-types` | ✅ | In-memory (no Docker) |
| `lab-conversation-history` | ✅ | — |
| `lab-context-management` | ✅ | — |
| `lab-external-memory` | ✅ | PersistentClient (local disk) |
| `lab-integration` | ✅ | PersistentClient (local disk) |

`lab-external-memory` and `lab-integration` use `chromadb.PersistentClient()`, which writes
to a local directory (`labs/memory-context/.chroma/`) without requiring a Docker service.
This enables cross-session persistence with no additional infrastructure beyond Ollama.

**Start Ollama (foundational profile):**

```bash
docker-compose --profile foundational up -d
```

**Install Python dependencies:**

```bash
pip install openai chromadb tiktoken
```

**Run a lab:**

```bash
cd labs/memory-context/lab-conversation-history
python main.py
```

---

## 4. Lab Structure

```text
labs/memory-context/
├── README.md                          ← this file
├── .chroma/                           ← ChromaDB persistent storage (gitignored)
├── shared/
│   ├── config.py                      ← Ollama client, token counter, budget constants
│   ├── history.py                     ← History manager (accumulate, count, enforce budget)
│   ├── context.py                     ← Context management strategies, context assembler
│   └── memory.py                      ← MemoryStore wrapper (ChromaDB PersistentClient)
├── lab-memory-types/
│   ├── README.md
│   └── main.py
├── lab-conversation-history/
│   ├── README.md
│   └── main.py
├── lab-context-management/
│   ├── README.md
│   └── main.py
├── lab-external-memory/
│   ├── README.md
│   └── main.py
└── lab-integration/
    ├── README.md
    └── main.py
```

Labs are isolated: each `main.py` imports only from `shared/` and the standard library.
No lab imports from another lab's directory.

---

## 5. Shared Module

All labs import from `labs/memory-context/shared/`. The shared module provides:

| Module | Exports | Purpose |
|--------|---------|---------|
| `config.py` | `build_client()`, `count_tokens()`, `HISTORY_BUDGET`, `MODEL`, `EMBED_MODEL` | Ollama client, token counting, budget constants |
| `history.py` | `HistoryManager` | Accumulates turns, tracks token count, signals budget threshold |
| `context.py` | `apply_sliding_window()`, `compress_history()`, `assemble_messages()` | Context management strategies and final prompt assembly |
| `memory.py` | `MemoryStore` | ChromaDB-backed episodic and semantic memory with embedding |

The `HistoryManager` is the single source of state for conversation history. All labs that
maintain multi-turn conversations use it rather than managing a raw list directly.

---

## 6. Mapping to Documentation

| Documentation | Lab | What the lab verifies |
|---------------|-----|-----------------------|
| `docs/memory-context/memory-types.md` | `lab-memory-types` | In-context memory loses early facts after overflow; external memory recalls them |
| `docs/memory-context/conversation-history.md` | `lab-conversation-history` | Token count grows per turn; budget ceiling prevents API errors |
| `docs/memory-context/context-management.md` | `lab-context-management` | Summarization preserves early-context recall accuracy better than truncation |
| `docs/memory-context/external-memory.md` | `lab-external-memory` | Episodes written in one process are retrieved in a separate process |
| `docs/memory-context/architecture.md` | `lab-integration` | All components compose without budget violation or retrieval failure |

---

## 7. Validation

**lab-memory-types**
```text
Expected: After 20+ turns, the in-context variant fails to recall a fact stated at turn 1
(or produces a wrong answer). The external memory variant recalls it correctly.
Token count is displayed after each turn.
```

**lab-conversation-history**
```text
Expected: 50-turn run completes without API errors.
Budget ceiling triggers at least once; oldest turn pair is dropped.
Token count and budget remaining are printed each turn.
```

**lab-context-management**
```text
Expected: Three strategy runs produce measurably different recall accuracy scores
when a fact-checking question is asked at turn 25 about content from turn 3.
Summarization recall ≥ truncation recall in all runs.
Compression event latency is displayed when triggered.
```

**lab-external-memory**
```text
Expected (run 1): Episode stored; semantic fact written; retrieval confirms entry exists.
Expected (run 2): Episode from run 1 retrieved with similarity score ≥ 0.75.
Expected (run 3): Updated semantic fact retrieved instead of original.
```

**lab-integration**
```text
Expected: 30-turn conversation runs without budget violation.
Memory entries are written after each turn (async log visible).
Restarting the script and resuming the conversation demonstrates cross-session recall.
```

---

## 8. Common Issues

**`chromadb` not installed.** Install with `pip install chromadb`. The package bundles its
own sqlite3 dependency; no separate database installation is required.

**tiktoken model not found.** If `tiktoken.encoding_for_model()` raises a `KeyError` for
the model name, use `tiktoken.get_encoding("cl100k_base")` as a fallback. This encoding
is compatible with most current models including Ollama-served Mistral variants.

**Cross-session recall not working.** Verify that `lab-external-memory` used
`chromadb.PersistentClient(path=CHROMA_PATH)` and that the `.chroma/` directory exists
in `labs/memory-context/`. If the directory is missing, the previous session's data was
not persisted.

**Budget violation on first turn.** If the system prompt alone exceeds the configured
`HISTORY_BUDGET`, the budget constant in `shared/config.py` must be recalculated. Verify
that `SYSTEM_PROMPT_TOKENS` is measured against the actual system prompt in use.

**Role alternation error from provider.** If the API returns "invalid message format",
the history list contains two consecutive messages with the same role. This occurs when
a truncation step drops an odd number of messages. Ensure `compress_history()` and
`apply_sliding_window()` always remove complete turn pairs (user + assistant).

---

## 9. Engineering Notes

**Token counting is approximate for Ollama models.** tiktoken's `cl100k_base` encoding
overestimates token counts by 2–5% for Mistral-family models. The `SAFETY_MARGIN` constant
in `shared/config.py` is set to absorb this error. Do not reduce it below 200 tokens.

**ChromaDB PersistentClient stores data locally.** The `.chroma/` directory grows with
each lab run. Clear it between independent experiments to avoid retrieval interference
from prior runs: `rm -rf labs/memory-context/.chroma/`.

**Summarization quality varies by model.** The `compress_history()` function uses the
same Ollama model for both summarization and generation. Smaller models (7B) produce
adequate summaries but may omit low-salience facts. If recall accuracy in
`lab-context-management` is unexpectedly low, inspect the generated summary directly.

**Async memory write is simulated.** In the labs, "async" write is implemented as a
sequential call after the response is returned — not a true background thread. This
simplifies the lab code while preserving the architectural intent. Production systems
should use `asyncio` or a background task queue.

---

## 9. Next Steps

After completing these labs, proceed to `labs/ai-agents/README.md`. The agents module
extends the memory model introduced here with planning state, tool-use history, and
coordination state in multi-agent systems.

To deepen understanding of the embedding and retrieval mechanics used in
`lab-external-memory`, revisit `labs/rag/lab-embeddings/` and
`labs/rag/lab-retrieval-playground/`.
