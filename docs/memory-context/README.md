---
id: "memory-context-readme"
title: "Memory and Context Management"
type: "step-readme"
step: "memory-context"
path: "docs/memory-context/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "memory types"
  - "conversation history"
  - "context management"
  - "external memory"
  - "token budget"

prerequisites:
  - "rag"

next:
  - "docs/memory-context/memory-types.md"

related:
  - "docs/rag/context-assembly.md"
  - "docs/llm-fundamentals/context-window.md"
  - "docs/ai-agents/README.md"

implementation_refs:
  - "labs/memory-context/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Introduces the memory model for LLM applications and the strategies for managing conversation state across single and multi-turn interactions."
---

## 1. Overview

LLM APIs are stateless. Every call starts from zero — the model has no memory of previous
interactions unless the application explicitly provides it. This module covers how to build
memory into LLM applications: what to remember, where to store it, and how to retrieve it
without exhausting the context window.

The capability this module unlocks is building applications that maintain coherent state
across multiple turns and across sessions — from a simple chatbot that remembers the last
ten messages to an enterprise assistant that recalls user preferences from months ago.

---

## 2. Scope

**Covered:**
- The memory model for LLM systems: types, trade-offs, and selection criteria
- Managing conversation history as a token-bounded data structure
- Context management strategies when conversation grows beyond the window
- External memory stores for long-term and cross-session recall

**Not covered:**
- Agent-level memory and planning (covered in `ai-agents`)
- RAG pipelines over external knowledge bases (covered in `rag`)
- Fine-tuning as a form of permanent memory (covered in `llm-fundamentals`)

---

## 3. Key Concepts

**Memory types** — LLM applications can draw on four distinct memory mechanisms:
in-context memory (the active context window), external memory (vector stores and
databases), parametric memory (model weights, read-only at runtime), and a combination
of episodic and semantic stores for structured long-term recall.

**Conversation history** — a stateful list of prior turns maintained by the application
and injected into every API call. It grows with each exchange and must be managed to stay
within the context window budget.

**Token budget** — the number of tokens available for conversation history and retrieved
context, after reserving space for the system prompt and expected output. Budget pressure
is the core engineering constraint of multi-turn applications.

**Context management** — the set of strategies for keeping the conversation window within
budget: sliding window truncation, summarization-based compression, and hybrid approaches.
Each trades recency against completeness.

**External memory** — information persisted outside the model in a vector store or database,
retrieved on demand by semantic similarity. Enables recall that survives beyond the context
window and across sessions.

---

## 4. Concept Map

```text
                    ┌─────────────────────────────────┐
                    │        LLM Application           │
                    └──────────────┬──────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                     ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │  In-context       │  │   Conversation   │  │  External Memory │
    │  Memory           │  │   History        │  │  (vector store)  │
    │  (context window) │  │   Manager        │  │                  │
    └──────────────────┘  └────────┬─────────┘  └────────┬─────────┘
                                   │                      │
                          ┌────────▼─────────┐   ┌───────▼──────────┐
                          │  Token Budget    │   │  Memory Retrieval │
                          │  Calculator      │   │  (semantic query) │
                          └────────┬─────────┘   └───────┬──────────┘
                                   │                      │
                          ┌────────▼──────────────────────▼──────────┐
                          │               Context Assembler           │
                          └───────────────────────────────────────────┘
```

---

## 5. Learning Flow

```text
memory-types.md          → What memory mechanisms exist and when to use each
conversation-history.md  → How to manage the history list and its growth
context-management.md    → Strategies for staying within the token budget
external-memory.md       → Long-term memory with vector stores (optional)
architecture.md          → How all components compose into a memory-aware system
implementation-reference.md → Implementation patterns across the labs
validation.md            → Criteria for completing this module
```

Topics 1–3 are required and sequential. `external-memory.md` builds on the first three
and is required for a complete understanding of production memory architectures. The
architecture document synthesizes all four.

---

## 6. Documentation Structure

```text
docs/memory-context/
├── README.md                    ← this file
├── memory-types.md              ← topic: memory mechanisms and selection
├── conversation-history.md      ← topic: history accumulation and management
├── context-management.md        ← topic: token budget and truncation strategies
├── external-memory.md           ← topic: vector store-backed long-term memory
├── architecture.md              ← system architecture
├── implementation-reference.md  ← implementation patterns
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-memory-types` | observation | Observe in-context vs external memory behavior with identical queries |
| `lab-conversation-history` | implementation | Build a multi-turn conversation manager with history accumulation |
| `lab-context-management` | implementation | Implement sliding window, truncation, and summarization strategies |
| `lab-external-memory` | implementation | Store and retrieve conversation episodes from a vector store |
| `lab-integration` | module-integration | Assemble all components into a memory-aware conversational application |

---

## 8. How to Use This Module

Follow topics in sequence: memory-types → conversation-history → context-management.
These three topics are tightly coupled — context-management builds directly on the history
structure introduced in conversation-history.

`external-memory.md` requires familiarity with embedding and vector search from the `rag`
module. If you completed `rag`, proceed directly. If not, read
`docs/rag/embeddings-and-vector-search.md` and `docs/rag/retrieval-strategies.md` first.

Run each lab immediately after reading its corresponding topic. The labs share a
`shared/` module — read the labs README before running individual labs.

---

## 9. Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `llm-fundamentals` | Context window and token limits are prerequisites |
| `llm-apis` | Conversation accumulation pattern is the foundation of history management |
| `rag` | External memory retrieval reuses embedding and vector search patterns |
| `ai-agents` | Agents extend this module's memory model with planning and tool-use state |

---

## 10. Next Steps

Begin with `docs/memory-context/memory-types.md` to understand the memory landscape
before working with specific implementations.
