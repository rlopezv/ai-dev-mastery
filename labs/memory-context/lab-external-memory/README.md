---
id: "lab-external-memory"
title: "External Memory — Episodic and Semantic Storage with ChromaDB"
type: "lab-readme"
step: "memory-context"
path: "labs/memory-context/lab-external-memory/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "external memory"
  - "episodic memory"
  - "semantic memory"
  - "write-retrieve-inject pattern"
  - "cross-session recall"

prerequisites:
  - "docs/memory-context/external-memory.md"
  - "labs/memory-context/lab-conversation-history"

related:
  - "docs/memory-context/memory-types.md"
  - "docs/memory-context/architecture.md"

summary: "Implementation lab — writes and retrieves episodic and semantic memory entries across separate process runs using ChromaDB PersistentClient."
---

## Overview

This lab implements the write-retrieve-inject pattern using ChromaDB's
`PersistentClient`, which stores data on local disk. Three sequential runs
demonstrate the full lifecycle of external memory:

| Run | Action |
|-----|--------|
| Run 1 | Write an episode and a semantic fact; verify immediate retrieval |
| Run 2 | Retrieve the episode from run 1 without re-writing it |
| Run 3 | Upsert (update) the semantic fact and verify the new value is returned |

All three runs execute in a single `python main.py` invocation. Run 2 will show
the cross-session effect most clearly if you restart the script after run 1.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| Episodic memory | `store.add_episode()` — timestamped conversation turn |
| Semantic memory | `store.upsert_fact()` — named fact, keyed for update |
| Write-retrieve-inject | Runs 1–3: write → retrieve → confirm value |
| Cross-session recall | Run 2: PersistentClient data survives process exit |
| Upsert | Run 3: same key overwrites previous embedding and value |

---

## Setup

```bash
docker-compose --profile light up -d
pip install openai chromadb tiktoken
```

The ChromaDB `PersistentClient` writes to `labs/memory-context/.chroma/`.
No additional Docker service is required.

---

## Run

```bash
cd labs/memory-context/lab-external-memory
python main.py
```

To observe cross-session recall, run the script twice:

```bash
python main.py  # run 1 writes; run 2 finds 0 prior episodes in the store
python main.py  # run 2 finds the episode written in the previous invocation
```

To reset the store between experiments:

```bash
rm -rf labs/memory-context/.chroma/
```

---

## Expected Output

### First invocation

```
RUN 1 — Write episode and semantic fact
[episode] stored id='ep-fraud-pipeline' | count=1
[fact]    stored key='user_domain' | count=1
[verify]  episode retrieved: distance=0.0000
[verify]  fact retrieved: 'user_domain' → 'fraud detection, streaming systems' | distance=0.1234
[run 1]   PASS — entries written and immediately retrievable

RUN 2 — Cross-session recall of episode from run 1
[state]   episode_count=1, fact_count=1
[retrieval] id='ep-fraud-pipeline'
[retrieval] distance=0.0712
[retrieval] text='User said: I am building a fraud detection pipeline...'
[run 2]   PASS — cross-session recall succeeded (distance <= 0.25)

RUN 3 — Upsert: update existing semantic fact
[before]  key='user_domain' value='fraud detection, streaming systems'
[upsert]  key='user_domain' updated with extended value
[after]   key='user_domain' value='fraud detection, streaming systems, real-time ML inference'
[run 3]   PASS — updated fact retrieved correctly
```

### Second invocation (cross-session effect)

Run 2 shows that the episode from the first invocation is already in the store
with a retrieval distance ≤ 0.25 — no writes were needed in this session.

---

## What to Look For

**Episode distance in run 1:** the distance is 0.0000 because the exact stored
text is used as the query. In run 2, the query differs ("streaming transaction
processing" vs the stored text), so the distance rises to 0.05–0.20.

**Upsert behavior in run 3:** ChromaDB's `upsert()` replaces both the document
text and its embedding when the ID matches. The old value is no longer retrievable.
This is the expected behavior for semantic facts that can be updated (e.g., user
preferences, project state).

**Cross-session recall failure:** if run 2 reports 0 episodes, the `.chroma/`
directory was cleared between runs or the PersistentClient path does not match.
Verify `CHROMA_PATH` in `shared/config.py`.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`mistral`) | Not used directly — model used by MemoryStore for chat context |
| Ollama (`nomic-embed-text`) | Embedding for storage and retrieval |
| ChromaDB `PersistentClient` | Disk-backed store — no Docker service required |
