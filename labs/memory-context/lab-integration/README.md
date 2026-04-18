---
id: "lab-integration"
title: "Memory-Aware Application — Integration"
type: "lab-readme"
step: "memory-context"
path: "labs/memory-context/lab-integration/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "conversation history"
  - "token budget"
  - "summarization-based compression"
  - "external memory"
  - "episodic memory"
  - "write-retrieve-inject pattern"
  - "cross-session recall"

prerequisites:
  - "docs/memory-context/architecture.md"
  - "labs/memory-context/lab-conversation-history"
  - "labs/memory-context/lab-context-management"
  - "labs/memory-context/lab-external-memory"

related:
  - "docs/memory-context/implementation-reference.md"

summary: "Module-integration lab — assembles HistoryManager, summarization compression, and MemoryStore into a 30-turn memory-aware conversational application."
---

# Memory-Aware Application — Integration

## Navigation

[Labs](../../README.md) / [Memory and Context Management — Labs](../README.md) / Memory-Aware Application — Integration

---


## Overview

This lab composes all memory-context components into a single working application.
It runs a 30-turn conversation simulating a realistic multi-session use case
(building a legal document review assistant), then validates that the system
correctly recalls facts stated early in the conversation.

**Components assembled:**
- `HistoryManager` — accumulates turns, tracks token count
- `compress_history()` — fires at threshold, preserves early facts via summarization
- `MemoryStore` — writes each turn as an episode; retrieves relevant context before each reply
- `assemble_messages()` — combines system prompt, retrieved memory, and history into the API call

**What you will observe:**
- Summarization fires at least once before turn 30 (if default budget is reached)
- Memory injection is logged whenever relevant episodes are retrieved
- Recall questions at turns 28–30 are answered correctly using injected memory

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| Conversation history | `HistoryManager` — single source of turn state |
| Compression threshold | `manager.at_threshold` — triggers summarization |
| Summarization | `compress_history()` — older turns distilled before recall |
| Episodic memory write | `store.add_episode()` — every turn stored after generation |
| Episodic memory retrieve | `store.retrieve_episodes()` — top-2 relevant episodes injected |
| Memory injection | `assemble_messages(..., memory_context=...)` — prepended to system prompt |
| Cross-session recall | `PersistentClient` — store survives restart |

---

## Setup

```bash
docker-compose --profile foundational up -d
pip install openai chromadb tiktoken
```

The ChromaDB `PersistentClient` writes to `labs/memory-context/.chroma/`.

---

## Run

```bash
cd labs/memory-context/lab-integration
python main.py
```

To test cross-session recall, run the script twice. On the second run, turn 1
should trigger memory injection from the previous session's episodes.

To reset the store:

```bash
rm -rf labs/memory-context/.chroma/
```

---

## Expected Output

```
Starting 30-turn memory-aware conversation
Budget: 7220 tokens | Episodes in store: 0
------------------------------------------------------------
[turn 01] tokens: 95 / 7220 (remaining: 7125) | ok
[turn 02] tokens: 182 / 7220 (remaining: 7038) | ok
...
[turn NN] SUMMARIZATION applied | tokens after: XXXX
...
[turn 25] tokens: XXXX / 7220 (remaining: XXX) | ok [memory injected]
...
[turn 30] tokens: XXXX / 7220 (remaining: XXX) | ok [memory injected]
------------------------------------------------------------
Conversation complete: 30 turns | episodes stored: 30

RECALL VALIDATION (turns 28–30)
[turn 28 Q] Can you remind me: what is my name and what project am I building?
[turn 28 A] Your name is Jordan and you are building an AI assistant for legal document review.
[turn 29 Q] What was the first technical challenge I mentioned at the start of our conversation?
[turn 29 A] The first challenge you mentioned was that legal documents can be very long — sometimes 200 pages.
[turn 30 Q] What is our target latency and what caching strategy did we decide on?
[turn 30 A] Your target latency is under 3 seconds and you are using Redis for caching.
```

**Budget violation:** if the script raises `openai.BadRequestError`, the token
budget is too small for the model's context window. Set `CONTEXT_WINDOW` to
match the model's actual window:

```bash
CONTEXT_WINDOW=8192 python main.py
```

**No memory injected:** if no turns show `[memory injected]`, retrieval distances
are above 0.35. This may indicate that `nomic-embed-text` is not running. Verify
with `ollama list`.

---

## What to observe

- **Memory injection:** turns showing `[memory injected]` indicate retrieved episodes with distance ≤ 0.35; early turns will not trigger injection (no stored episodes yet); later turns should trigger it as the store fills
- **Summarization event:** at least one `SUMMARIZATION applied` line should appear; note the token count before and after — compression reduces it significantly
- **Recall accuracy:** turns 28–30 answers should name "Jordan", reference the legal document challenge and the target latency, and mention "Redis"; these rely on injected memory, not in-context history

## Concepts verified

- [ ] Memory injection logged on at least one turn after turn 5
- [ ] Summarization fires at least once before turn 30
- [ ] Recall turn 28 answer contains "Jordan" and references the legal document review project
- [ ] Recall turn 30 answer references the target latency and the caching strategy

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `run_integration()`, comment out the `store.add_episode()` call at the end of the loop
- **Expected degradation:**
  - No episodes are ever written; `[memory injected]` never appears
  - Recall turns 28–30 rely entirely on in-context history and summarization
  - If compression has dropped the early turns, recall fails — model cannot name "Jordan" or recall the Redis caching decision
  - Shows that the write step of the write-retrieve-inject cycle is required

Restore `store.add_episode()` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`mistral`) | Chat completions and summarization |
| Ollama (`nomic-embed-text`) | Embedding for episode storage and retrieval |
| ChromaDB `PersistentClient` | Disk-backed episodic memory — no Docker service required |
