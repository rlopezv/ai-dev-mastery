---
id: "memory-context-memory-types"
title: "Memory Types in LLM Applications"
type: "topic"
step: "memory-context"
path: "docs/memory-context/memory-types.md"
status: "draft"
level: "intermediate"

concepts:
  - "memory types"
  - "in-context memory"
  - "external memory"
  - "episodic memory"
  - "semantic memory"
  - "parametric memory"

prerequisites:
  - "docs/llm-fundamentals/context-window.md"
  - "docs/llm-apis/api-patterns.md"

next:
  - "docs/memory-context/conversation-history.md"

related:
  - "docs/rag/rag-fundamentals.md"
  - "docs/llm-fundamentals/fine-tuning.md"

implementation_refs:
  - "labs/memory-context/lab-memory-types"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the four memory mechanisms available to LLM applications, their storage locations, lifetimes, and the selection criteria that determine which type to use."
---

# Memory Types in LLM Applications

## Navigation

[Docs](../README.md) / [Memory and Context Management](README.md) / Memory Types in LLM Applications

---

## 1. Intuition

A human conversation relies on multiple kinds of memory simultaneously: what was just said
(working memory), what has been discussed in previous meetings (episodic), facts about the
other person (semantic), and deeply ingrained skills (procedural). LLM applications face
the same requirement but must engineer each type explicitly — the model itself provides
only one, and it resets after every call.

---

## 2. Explanation

### 2.1 Why

LLM inference is stateless. The model receives tokens in and produces tokens out. Between
calls, nothing is retained. An application that needs to maintain state — a user's name,
the outcome of a previous request, preferences accumulated over weeks — must decide where
to store that state, for how long, and how to surface it to the model when it is needed.

Choosing the wrong memory mechanism produces predictable failures: a chatbot that forgets
the user's name after ten messages (context overflow), an assistant that repeats the same
suggestions because it has no record of past sessions (missing episodic store), or a
knowledge base that goes stale because it encodes facts in weights rather than a
retrievable store (parametric dependency).

### 2.2 How

Four memory mechanisms are available to LLM applications:

**In-context memory** is the content currently in the active context window — the system
prompt, conversation history, and any injected documents. It is the only memory the model
can reason over directly. It is fast, zero-latency, and supports arbitrary content, but it
is bounded by the context window size and destroyed at the end of each session. Every other
memory type exists to compensate for these two limits.

**External memory** is information stored in a vector store, relational database, or
key-value store outside the model. It is retrieved on demand and injected into the context
window for the relevant call. Capacity is unlimited — only retrieved fragments consume
context window space. The retrieval step adds latency (typically 10–100ms for a vector
search) and requires a write step when new information needs to be persisted.

**Episodic memory** is a specialization of external memory that stores records of past
conversation turns or events, indexed by time and semantic content. It is queried when the
current conversation requires recall of what happened in a previous session. The entry
format is typically a compressed summary of a past turn plus its timestamp and key entities.

**Semantic memory** is a specialization of external memory that stores facts about
entities — users, products, domains — without temporal ordering. It is queried when the
application needs to personalize a response based on durable attributes: a user's
preferences, an account's industry, a product's specifications. Semantic memory entries are
updated when facts change, not appended chronologically.

**Parametric memory** refers to the knowledge encoded in the model's weights during
training. It is always present and zero-latency but completely static at runtime — it does
not change unless the model is retrained or fine-tuned. It cannot be updated with
application-specific data without retraining and cannot be queried selectively. It is not
a practical mechanism for application-layer memory management.

### 2.3 Code example

```python
# See: labs/memory-context/lab-memory-types/main.py

# In-context memory: inject history directly into the API call
def call_with_history(client, history: list[dict], user_message: str) -> str:
    messages = history + [{"role": "user", "content": user_message}]
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

# External memory: retrieve relevant episodes before calling the model
def call_with_external_memory(client, memory_store, user_message: str) -> str:
    episodes = memory_store.search(user_message, top_k=3)   # semantic retrieval
    context = "\n".join(ep["summary"] for ep in episodes)
    system = f"Relevant past context:\n{context}"
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user_message}]
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content
```

---

## 3. Memory Type Comparison

| Type | Storage | Lifetime | Capacity | Latency | Updatable |
|------|---------|----------|----------|---------|-----------|
| In-context | Context window | Single session | Context window limit | None | Yes (append) |
| External — episodic | Vector store / DB | Persistent | Unlimited | 10–100ms | Yes (append) |
| External — semantic | Vector store / DB | Persistent | Unlimited | 10–100ms | Yes (overwrite) |
| Parametric | Model weights | Permanent | Fixed at training | None | Retrain only |

---

## 4. Engineering Implications

**In-context memory pressure** is the primary constraint in multi-turn applications.
Every turn adds tokens. A conversation of 50 exchanges with 200 tokens per turn consumes
10,000 tokens before any system prompt or retrieved content is counted. For a model with a
32k context window, this leaves 22k tokens for other uses — a constraint that tightens
further in RAG-augmented systems.

**External memory introduces retrieval quality risk.** If the wrong episodes are retrieved
or no relevant episodes are found, the model produces a response as if it has no memory at
all — silently, without error. The application must monitor retrieval hit rates and relevance
scores to detect degradation.

**Parametric memory is not controllable at runtime.** A model may confidently produce
outdated facts because they are encoded in its weights. Applications that require accuracy
on time-sensitive or domain-specific knowledge should not rely on parametric memory — they
should use external memory or RAG.

**Mixing types requires explicit assembly.** When both conversation history (in-context)
and external memory (retrieved episodes) are used together, the context assembler must
decide how to allocate the token budget between them. There is no default strategy — the
application must implement one.

---

## 5. Implementation Connection

`lab-memory-types` demonstrates the observable difference between in-context and external
memory by running identical multi-turn conversations under two conditions: one where history
lives entirely in the context window, and one where older turns are moved to a vector store
and retrieved selectively. The lab makes the token count, retrieval latency, and recall
accuracy visible for comparison.

---

## 6. Failure Modes and Limitations

**Context overflow with no fallback.** An application that appends every turn to the history
list without a budget ceiling will eventually exceed the context window and either receive
an API error or silently truncate input. Budget enforcement must be designed in, not added
later.

**Stale semantic memory.** An external semantic memory store that is never updated will
diverge from reality. If a user changes their preferences and the store is not updated, the
application will personalize based on outdated facts. Write-back logic is as important as
retrieval logic.

**Retrieval miss on first turn.** External memory requires prior content to retrieve from.
On the first session, or after a long gap with no stored episodes, retrieval returns nothing
useful. The application must handle the cold-start case explicitly — typically by
defaulting to in-context only for the first few turns.

---

## 7. Summary

LLM applications can draw on four memory mechanisms: in-context (active context window),
external episodic (past conversation records), external semantic (entity facts), and
parametric (model weights). Only in-context memory is reasoned over directly by the model
— all other types must be retrieved and injected before each call. The core engineering
constraint is the context window budget, which bounds what can be held in memory at any
given moment and drives the design of every other memory strategy covered in this module.
