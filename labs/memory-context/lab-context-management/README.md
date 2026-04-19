---
id: "lab-context-management"
title: "Context Management — Truncation, Sliding Window, Summarization"
type: "lab-readme"
step: "memory-context"
path: "labs/memory-context/lab-context-management/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "truncation"
  - "sliding window"
  - "summarization-based compression"
  - "compression threshold"
  - "recall accuracy"

prerequisites:
  - "docs/memory-context/context-management.md"
  - "labs/memory-context/lab-conversation-history"

related:
  - "docs/memory-context/conversation-history.md"

summary: "Implementation lab — runs the same 25-turn conversation under three context management strategies and measures which strategy best preserves recall of an early-context fact."
---

# Context Management — Truncation, Sliding Window, Summarization

## Navigation

[Labs](../../README.md) / [Memory and Context Management — Labs](../README.md) / Context Management — Truncation, Sliding Window, Summarization

---


## Overview

This lab runs three identical 25-turn conversations — one per context management
strategy — and measures how well each strategy preserves a fact stated at turn 3
when asked about it at turn 25.

**Strategies compared:**
1. **Truncation** — drop oldest pairs when threshold is hit
2. **Sliding window** — keep the last 8 turn pairs, drop the rest
3. **Summarization** — compress older turns into a summary, keep recent turns verbatim

**What you will observe:**
- Compression event timing (latency logged when each strategy fires)
- Final recall reply for each strategy at turn 25
- Summary table showing PASS/FAIL for each strategy

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| Compression threshold | `manager.at_threshold` — checked each turn |
| Truncation | `apply_truncation()` — drops oldest pairs |
| Sliding window | `apply_sliding_window()` — retains last N pairs |
| Summarization | `compress_history()` — distills older turns, keeps recent ones |
| Recall accuracy | `score_recall()` — keyword check for "Nighthawk" and "16" |

---

## Setup

```bash
docker-compose --profile foundational up -d
pip install openai tiktoken
```

---

## Run

```bash
cd labs/memory-context/lab-context-management
python main.py
```

The script runs all three strategies sequentially. Total runtime is approximately
3–5 minutes depending on model and hardware.

---

## Expected Output

```
STRATEGY: TRUNCATION
[turn 03] tokens: ...
...
[turn NN] TRUNCATION applied | latency: X.Xms
...
[recall]  What is the project name and how many nodes does the cluster have?
[reply]   I don't have that information in our current conversation...

STRATEGY: SLIDING_WINDOW
...
[turn NN] SLIDING WINDOW applied | latency: X.Xms
...
[reply]   I don't recall that information from our conversation...

STRATEGY: SUMMARIZATION
...
[turn NN] SUMMARIZATION applied | latency: XXXXms
...
[reply]   The project is called Nighthawk and it runs on a 16-node Kubernetes cluster.

============================
RECALL ACCURACY SUMMARY
truncation           FAIL
sliding_window       FAIL
summarization        PASS
Expected: summarization recall >= truncation recall
```

**Summarization latency** is higher than truncation (200–2000ms vs <1ms) because
it requires a synchronous API call to generate the summary.

**Truncation and sliding window** are expected to FAIL recall because the anchor
fact (stated at turn 3) falls outside the retained window by turn 25.

**Summarization** is expected to PASS because the LLM distills the anchor fact
into the summary before dropping old turns.

---

## What to observe

**Compression event turns:** the strategy fires when `at_threshold` is True
(token count ≥ 80% of budget). With the default 8192-token window this may not
trigger before turn 25. If it does not trigger, add `CONTEXT_WINDOW=2000` to
force earlier compression:

```bash
CONTEXT_WINDOW=2000 python main.py
```

**Summarization quality:** inspect the `[reply]` for the summarization strategy.
If the recall fails, read the summary message inserted into history — smaller
models (7B) may omit low-salience facts. Increasing `keep_recent_pairs` in
`compress_history()` has no effect on recall of early facts; the summary quality
is the limiting factor.

## Concepts verified

- [ ] Summarization strategy recalls "Nighthawk" and "16" at turn 25 (PASS)
- [ ] Truncation and sliding window fail recall (FAIL) — anchor from turn 3 was dropped
- [ ] Summarization latency is higher than truncation (200ms+ vs <1ms)

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `FILLER_TURNS`, move `ANCHOR_FACT` from index 2 (turn 3) to index 22 (turn 23) — near the end of the list
- **Expected degradation:**
  - All three strategies retain the anchor fact because it now falls within the recent window
  - All three strategies PASS recall — the PASS/FAIL distinction collapses
  - The lab no longer demonstrates that only summarization preserves early-context facts

Restore `ANCHOR_FACT` at index 2 after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama (`mistral`) | Chat completions and summarization |
