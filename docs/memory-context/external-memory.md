---
id: "memory-context-external-memory"
title: "External Memory"
type: "topic"
step: "memory-context"
path: "docs/memory-context/external-memory.md"
status: "draft"
level: "intermediate"

concepts:
  - "external memory"
  - "episodic memory"
  - "semantic memory"
  - "memory retrieval"
  - "memory compression"

prerequisites:
  - "docs/memory-context/context-management.md"
  - "docs/rag/embeddings-and-vector-search.md"

next:
  - "docs/memory-context/architecture.md"

related:
  - "docs/rag/retrieval-strategies.md"
  - "docs/rag/context-assembly.md"

implementation_refs:
  - "labs/memory-context/lab-external-memory"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how to persist conversation episodes and entity facts in a vector store for cross-session recall, covering the write, retrieval, and injection pattern that extends in-context memory beyond a single session."
---

# External Memory

## Navigation

[Docs](../README.md) / [Memory and Context Management](README.md) / External Memory

---

## 1. Intuition

In-context memory resets when the session ends. External memory persists across sessions
the same way a notebook outlasts a single meeting: you write down what matters during the
session, and you look it up before the next one. The retrieval step is the cost — you pay
it selectively, only for what the current conversation actually needs.

---

## 2. Explanation

### 2.1 Why

In-context memory and context management strategies (sliding window, summarization) address
token budget pressure within a single session. They do not address cross-session continuity.
When a user returns after a week, the history list is empty — the previous conversation is
gone. For applications that need to remember who the user is, what they have asked before,
or what decisions were made in prior sessions, external memory is the only mechanism that
works.

External memory also addresses scale. A user with 200 past sessions has far more history
than any context window can hold. External memory stores all of it and retrieves only the
fraction relevant to the current query — the same pattern RAG uses for document corpora,
applied to conversation history.

### 2.2 How

External memory follows a three-step pattern: **write**, **retrieve**, and **inject**.

**Write.** At the end of a conversation turn or session, the application stores a memory
entry in a vector store. Each entry is embedded and indexed for later semantic retrieval.

Two entry types serve different purposes:

- **Episodic entries** record what happened: a conversation summary, a decision made, a
  task completed. They are appended chronologically and never overwritten.
- **Semantic entries** record facts about entities: user preferences, account attributes,
  domain facts. They are updated when the fact changes, not appended.

```python
# See: labs/memory-context/lab-external-memory/main.py

def write_episode(memory_store, session_id: str, summary: str, metadata: dict) -> None:
    entry = {
        "text": summary,
        "metadata": {"session_id": session_id, "type": "episode", **metadata}
    }
    memory_store.add(entry)

def write_semantic_fact(memory_store, entity_id: str, fact: str) -> None:
    # Overwrite existing fact for this entity if present
    memory_store.upsert(
        id=entity_id,
        text=fact,
        metadata={"type": "semantic", "entity": entity_id}
    )
```

**Retrieve.** At the start of a new session or when the user's message suggests prior
context is relevant, the application queries the vector store by semantic similarity to the
current query.

```python
def retrieve_relevant_memory(memory_store, query: str, top_k: int = 3) -> list[dict]:
    results = memory_store.search(query, top_k=top_k)
    return [r for r in results if r["score"] >= MEMORY_RELEVANCE_THRESHOLD]
```

**Inject.** Retrieved entries are injected into the system prompt or as context messages
before the user's current message. The injection format signals to the model that the
content is recalled context, not live conversation:

```python
def build_memory_context(episodes: list[dict]) -> str:
    if not episodes:
        return ""
    lines = ["Relevant context from previous sessions:"]
    for ep in episodes:
        lines.append(f"- {ep['text']}")
    return "\n".join(lines)
```

**What to store.** Not every turn warrants a memory write. A useful heuristic:

- Store: stated goals, decisions, constraints, preferences, completed tasks
- Skip: clarifying questions, greetings, exploratory turns with no outcome

The write step is most reliable when triggered by the model itself: after each turn, ask
the model whether anything from this turn should be remembered and what the entry should
say. This delegates the signal extraction to the model rather than implementing heuristic
filters in application code.

### 2.3 Code example

```python
# See: labs/memory-context/lab-external-memory/main.py

REMEMBER_PROMPT = """Review this conversation turn and decide if it contains
information worth remembering for future sessions.

User: {user_message}
Assistant: {assistant_reply}

If yes, write a one-sentence memory entry capturing the key fact or decision.
If no, reply with SKIP."""

def extract_memory(client, user_message: str, assistant_reply: str) -> str | None:
    response = call_model(client, REMEMBER_PROMPT.format(
        user_message=user_message, assistant_reply=assistant_reply
    ))
    return None if response.strip() == "SKIP" else response.strip()
```

---

## 3. External Memory vs In-Context Management

| Dimension | In-context + management | External memory |
|-----------|------------------------|-----------------|
| Scope | Single session | Cross-session |
| Capacity | Context window | Unlimited |
| Retrieval | Always injected | On-demand |
| Write cost | None (append) | Embedding + index write |
| Read latency | None | 10–100ms per query |
| Consistency | Exact | Depends on retrieval accuracy |
| Cold start | Instant | Empty on first session |

---

## 4. Engineering Implications

**Retrieval accuracy determines memory quality.** An external memory store is only useful
if the retrieval step surfaces the right entries. A low relevance threshold returns too much
noise; a high threshold misses relevant context. The threshold should be calibrated against
a sample of real queries and evaluated with recall metrics, not set arbitrarily.

**Write timing affects consistency.** Writing memory entries after the model responds, in
the same request-response cycle, adds latency to every turn. Writing asynchronously (after
the response is sent to the user) keeps turn latency low but means the new entry is not
available if the user sends another message immediately. For most applications, asynchronous
write is the right default.

**Semantic entries require an update strategy.** An episodic entry is always correct at
the time of writing — it records what happened. A semantic entry may become stale: the user
changed their preference, the account migrated to a new plan. The application must decide
when to overwrite (upsert by entity ID) versus append (treating each fact change as a new
episode). Mixing the two strategies for different fact types is common in production systems.

**Memory grows unboundedly without a retention policy.** Over months of use, an external
memory store accumulates hundreds of entries per user. Without a retention policy — expiring
entries older than N days, capping entries per user, or merging similar entries — retrieval
recall degrades as the store fills with outdated or redundant content.

---

## 5. Implementation Connection

`lab-external-memory` implements the full write–retrieve–inject cycle using ChromaDB as the
vector store and Ollama for embeddings. The lab simulates three sessions with the same user:
the first establishes facts (user preferences, a project goal), the second recalls and uses
them, and the third introduces a preference change and verifies the update propagates to
retrieval. The lab makes retrieval scores visible and demonstrates the cold-start behavior
on a clean store.

---

## 6. Failure Modes and Limitations

**Hallucinated memory injection.** If retrieved memory entries contain inaccurate summaries
— produced by a poor extraction prompt or an unreliable model — the application will inject
false context into future sessions. The model will treat injected content as fact and
produce responses grounded in hallucination. Memory write quality must be validated, not
assumed.

**Retrieval miss on low-signal queries.** Short, ambiguous queries ("what did we discuss?",
"as I mentioned") produce weak query embeddings with low discriminative power. The retrieval
step may return irrelevant or no entries even when highly relevant memory exists. The
injection step should detect empty results and omit the memory context block rather than
injecting a blank section.

**Session ID contamination.** If episodic entries from multiple users share the same vector
collection without user-scoped filtering, retrieval may surface another user's episodes. The
metadata filter on `user_id` must be applied at query time, not only at write time.

---

## 7. Summary

External memory extends in-context memory beyond a single session by persisting entries in
a vector store and retrieving them on demand. Episodic entries record events and are
appended; semantic entries record facts and are upserted. The write–retrieve–inject pattern
mirrors the RAG pipeline but applied to conversation state rather than document corpora. The
key engineering constraints are retrieval accuracy, write timing, semantic entry update
strategy, and the absence of a default retention policy. External memory is the foundation
for any LLM application that needs to recognize returning users, recall past decisions, or
maintain user-specific state across sessions.
