---
id: "lab-context-window"
title: "Context Window"
type: "lab-readme"
step: "llm-fundamentals"
path: "labs/llm-fundamentals/lab-context-window/README.md"
status: "draft"
level: "foundational"
concepts:
  - "context-window"
  - "token-budget"
prerequisites:
  - "docs/llm-fundamentals/context-window.md"
related:
  - "docs/llm-fundamentals/README.md"
summary: "Observation lab — measures token budget consumption per prompt component and validates tiktoken estimates against Ollama's reported prompt_eval_count."
---

# Context Window

## Navigation

[Labs](../../README.md) / [LLM Fundamentals — Labs](../README.md) / Context Window

---

## Overview

This lab measures token budget consumption before and after sending requests to Ollama. It shows that context window usage is predictable from the tokenizer and that `prompt_eval_count` in the API response confirms the pre-send estimate.

**Out of scope:** history truncation strategies, summarization, RAG-style retrieval injection (covered in `memory-context` and `rag`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `context-window` | `observe_progressive_fill()` — token count grows with each appended sentence, approaching the model limit |
| `token-budget` | `observe_component_costs()` — each prompt component (system, history, user, output) is counted and summed before the request |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# Install dependencies (from the module root):
pip install -r labs/llm-fundamentals/requirements.txt
```

---

## Run

```bash
cd labs/llm-fundamentals
python lab-context-window/main.py
```

---

## Expected Output

```
Model: llama3.2  |  Approximate context limit: 128000 tokens

=== Observation 1: Token cost per component ===
  System prompt:        40 tokens
  Conversation history: 42 tokens
  User message:         23 tokens
  ─────────────────────────────
  Total input:         105 tokens
  Max output:           64 tokens
  Grand total:         169 tokens

=== Observation 2: Estimate vs API token count ===
  Estimated (tiktoken):  10 tokens
  Reported (Ollama):     17 tokens
  Delta:                  7 tokens
  ✓ Estimates agree within 10 tokens (chat template overhead expected)

=== Observation 3: Progressive context fill (limit: 128000) ===
  Step   1 —    16 tokens (  0.0% of 128000-token limit)
  Step   2 —    32 tokens (  0.0% of 128000-token limit)
  Step   3 —    48 tokens (  0.0% of 128000-token limit)
  → Stopping fill at N tokens to stay within MAX_FILL_TOKENS=512
  prompt_eval_count (API): ...
```

---

## What to observe

- **Observation 1:** System prompts cost tokens on every request. A 40-token system prompt × 1,000 daily requests = 40,000 input tokens per day in overhead alone.
- **Observation 2:** The delta between tiktoken estimate and Ollama's `prompt_eval_count` reflects the chat template framing Ollama adds around the prompt. This is normal and expected — budget for it.
- **Observation 3:** Each appended sentence consumes a predictable number of tokens. The `MAX_FILL_TOKENS` cap prevents runaway growth during the observation.

---

## Concepts verified

- [ ] System prompt token cost is fixed and applies on every request — observable at Observation 1
- [ ] tiktoken estimate agrees with Ollama's `prompt_eval_count` within 10 tokens — observable at Observation 2
- [ ] Token count grows linearly as content is added — observable at Observation 3

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_progressive_fill()`, remove `NUM_PREDICT` from the stop condition — change `total_tokens + NUM_PREDICT + tokens_per_sentence > MAX_FILL_TOKENS` to `total_tokens + tokens_per_sentence > MAX_FILL_TOKENS`
- **Expected degradation:**
  - The fill loop consumes the full `MAX_FILL_TOKENS` budget with no output reservation
  - The API response is truncated or cut short because no tokens remain for generation

Restore the original stop condition after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | LLM inference server — provides `prompt_eval_count` to validate pre-send token estimates |
| tiktoken | Standalone tokenizer — computes component-level token counts before each request |
