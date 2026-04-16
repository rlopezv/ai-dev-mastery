---
id: "lab-conversation-history"
title: "Conversation History — Token-Bounded Multi-Turn Loop"
type: "lab-readme"
step: "memory-context"
path: "labs/memory-context/lab-conversation-history/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "conversation history"
  - "token counting"
  - "token budget"
  - "budget ceiling"
  - "truncation"

prerequisites:
  - "docs/memory-context/conversation-history.md"

related:
  - "docs/memory-context/context-management.md"

summary: "Implementation lab — builds a 50-turn conversation loop with explicit token tracking and budget ceiling enforcement using HistoryManager."
---

## Overview

This lab implements a token-bounded multi-turn chat loop using the `HistoryManager`
shared component. It runs 50 turns against Ollama and enforces a hard budget ceiling
by dropping the oldest turn pair whenever the count exceeds the configured limit.

**What you will observe:**
- Token count grows after every turn (logged each turn)
- At least one budget ceiling event triggers before the loop completes
- The script completes all 50 turns without an API error

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| Conversation history | `HistoryManager._history` — list of role/content dicts |
| Token counting | `manager.status_line()` — printed each turn |
| Budget ceiling | `manager.at_ceiling` — checked before each API call |
| Truncation | `manager.history[2:]` — oldest pair dropped when ceiling hit |

---

## Setup

```bash
docker-compose --profile light up -d
pip install openai tiktoken
```

---

## Run

```bash
cd labs/memory-context/lab-conversation-history
python main.py
```

---

## Expected Output

```
Starting 50-turn conversation loop
Budget: 7220 tokens
------------------------------------------------------------
[turn 01] tokens: 87 / 7220 (remaining: 7133) | ok
[turn 02] tokens: 163 / 7220 (remaining: 7057) | ok
...
[turn NN] BUDGET CEILING: oldest turn pair dropped
[turn NN] tokens: 6980 / 7220 (remaining: 240) | THRESHOLD
...
[turn 50] tokens: XXXX / 7220 (remaining: XXX) | ok
------------------------------------------------------------
Conversation complete: 50 turns, final token count: XXXX
```

- Token count increases each turn.
- `BUDGET CEILING` log line appears at least once.
- `THRESHOLD` appears when count exceeds 80% of budget.
- The loop completes without `openai.BadRequestError`.

---

## What to observe

- **Token growth rate:** count increases each turn as history accumulates; the rate depends on average reply length — longer model replies grow the count faster
- **Budget ceiling event:** note which turn triggers the ceiling; after the event, the token count drops as the oldest pair is removed, then resumes growing
- **Threshold marker:** turns with count at ≥ 80% of budget are labeled `THRESHOLD`; the ceiling guard fires on the turn that exceeds the hard limit

## Concepts verified

- [ ] Token count increases each turn
- [ ] At least one `BUDGET CEILING` event is logged before turn 50
- [ ] The script completes all 50 turns without `openai.BadRequestError`
- [ ] Token count after a ceiling event is lower than the count before

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `run_conversation()`, comment out the `if manager.at_ceiling:` block (the truncation guard)
- **Expected degradation:**
  - Token count grows unbounded — no pairs are ever dropped
  - The model eventually returns `openai.BadRequestError` when the context exceeds the API limit
  - The script raises before completing all 50 turns
  - Shows why the budget ceiling guard is required for long-running conversations

Restore the ceiling guard after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`mistral`) | Chat completions |
