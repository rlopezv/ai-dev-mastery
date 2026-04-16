---
id: "lab-memory-types"
title: "Memory Types — In-Context vs External"
type: "lab-readme"
step: "memory-context"
path: "labs/memory-context/lab-memory-types/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "in-context memory"
  - "external memory"
  - "token budget"
  - "truncation"

prerequisites:
  - "docs/memory-context/memory-types.md"

related:
  - "docs/memory-context/conversation-history.md"
  - "docs/memory-context/external-memory.md"

summary: "Observation lab — demonstrates in-context memory loss after truncation and external memory recall via ChromaDB embedding retrieval."
---

## Overview

This lab makes the difference between in-context and external memory observable.
It runs two back-to-back observations using the same conversation fixture: a small
token budget, a named anchor fact stated at turn 1, and ten filler turns that
overflow the context.

**What you will observe:**
- Observation 1: after truncation, the model cannot recall the anchor fact
- Observation 2: the same anchor fact is stored in ChromaDB at turn 1 and retrieved
  before the final question — the model recalls it correctly despite truncation

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| In-context memory | History list passed to every chat call |
| Token budget | `DEMO_HISTORY_BUDGET` — intentionally small to force overflow |
| Truncation | `drop_oldest_pair()` — removes oldest user+assistant pair when budget exceeded |
| External memory write | `collection.add()` with embedding at turn 1 |
| External memory retrieve | `collection.query()` before the recall question |
| Memory injection | Retrieved fact prepended to system prompt |

---

## Setup

**Requirements:** Ollama running with `mistral` and `nomic-embed-text` pulled.

```bash
docker-compose --profile light up -d
```

```bash
pip install openai chromadb tiktoken
```

---

## Run

```bash
cd labs/memory-context/lab-memory-types
python main.py
```

No environment variables are required. To override the model:

```bash
MODEL=llama3 EMBED_MODEL=nomic-embed-text python main.py
```

---

## Expected Output

### Observation 1 — In-context overflow

```
OBSERVATION 1 — In-context memory overflow
Anchor fact stated at turn 1: 'My name is Alex and I am working on a project called Falcon.'
Budget: 630 tokens  |  Window: 800 tokens
[turn 1]  anchor fact stated | tokens: 42 / 630
[turn 2]  tokens: 147 / 630
...
[turn N]  *** TRUNCATION: oldest turn pair dropped ***
...
[recall]  What is my name and what project am I working on?
[reply]   I don't have that information in our conversation...
```

The model's reply in the recall step does **not** mention "Alex" or "Falcon".
Token counts are printed each turn. At least one truncation event is logged before the recall.

### Observation 2 — External memory recall

```
OBSERVATION 2 — External memory preserves fact across overflow
[turn 1]  anchor fact stated | tokens: 42 / 630
[memory]  anchor fact written to ChromaDB collection
...
[turn N]  *** TRUNCATION: oldest turn pair dropped ***
...
[retrieval]  top result: 'My name is Alex and I am working on a project called Falcon.'
[retrieval]  distance: 0.0821 (lower = more similar)
[recall]  What is my name and what project am I working on?
[reply]   Your name is Alex and you are working on a project called Falcon.
```

The retrieval distance is below 0.20. The model's reply correctly names "Alex" and "Falcon".

---

## What to Look For

**Truncation timing:** the `*** TRUNCATION ***` log line shows the exact turn where the
anchor fact leaves the context window. After that point, Observation 1 has no access to it.

**Retrieval distance:** a distance below 0.20 indicates high semantic similarity between
the stored fact and the recall question. Values above 0.35 suggest the embedding model
is not well-suited to the query, or that `nomic-embed-text` is not running in Ollama.

**Reply quality:** Observation 1 may produce a hallucinated name or an explicit "I don't know".
Both are valid — what matters is the absence of "Alex" and "Falcon". Observation 2 should
reproduce the anchor fact verbatim or near-verbatim.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`mistral`) | Chat completions |
| Ollama (`nomic-embed-text`) | Embedding for storage and retrieval |
| ChromaDB `EphemeralClient` | In-memory store — no Docker, no persistence |

ChromaDB runs in-process. No `docker-compose` profile beyond `light` is needed.
The collection is discarded when the script exits.
