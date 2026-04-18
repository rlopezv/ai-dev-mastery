---
id: "lab-llm-anatomy"
title: "LLM Anatomy"
type: "lab-readme"
step: "llm-fundamentals"
path: "labs/llm-fundamentals/lab-llm-anatomy/README.md"
status: "draft"
level: "foundational"
concepts:
  - "inference-pipeline"
  - "transformer-architecture"
  - "tokenization"
prerequisites:
  - "docs/llm-fundamentals/llm-architecture.md"
related:
  - "docs/llm-fundamentals/README.md"
summary: "Observation lab — makes the transformer inference pipeline measurable via Ollama API telemetry: token counts, timing, and output scaling."
---

# LLM Anatomy

## Navigation

[Labs](../../README.md) / [LLM Fundamentals — Labs](../README.md) / LLM Anatomy

---

## Overview

This lab makes the transformer inference pipeline observable through the Ollama API. Behind the simple "send a prompt, get a response" interface, the API reports telemetry that maps directly to pipeline stages. The lab does not build an application — it isolates and measures four properties of the pipeline.

**Out of scope:** streaming, multi-turn conversation, inference parameter tuning.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `inference-pipeline` | `observe_single_generation()` — reads `prompt_eval_count`, `eval_count`, `total_duration` from the API response |
| `transformer-architecture` | `observe_token_count_stability()` — fixed input produces identical `prompt_eval_count` across runs |
| `tokenization` | `observe_output_token_scaling()` — `eval_count` is bounded by `num_predict`, confirming the autoregressive loop |

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
python lab-llm-anatomy/main.py
```

---

## Expected Output

```
Setup OK — Ollama reachable, model 'llama3.2' available

=== Observation 1: Available models ===
  name=llama3.2                       size=2019 MB

=== Observation 2: Single generation ===
Model:  llama3.2
Prompt: 'The transformer architecture processes tokens by computing self-attention'

--- Response ---
... (generated text) ...

--- Metadata ---
  prompt_eval_count (input tokens):  11
  eval_count        (output tokens): 128
  total_duration    (nanoseconds):   ...
  model:                             llama3.2

=== Observation 3: Token count stability (3 runs) ===
  Run 1: prompt_eval_count = 11
  Run 2: prompt_eval_count = 11
  Run 3: prompt_eval_count = 11
  ✓ Stable — all runs report 11 input tokens

=== Observation 4: Output token scaling ===
  num_predict=8    → eval_count=8    response='...first 8 tokens...'
  num_predict=32   → eval_count=32   response='...first 32 tokens...'
  num_predict=128  → eval_count=...  response='...'
```

---

## What to observe

- `prompt_eval_count` — number of input tokens processed. Identical across runs for the same prompt (Observation 3).
- `eval_count` — number of output tokens generated. Never exceeds `num_predict` (Observation 4).
- `total_duration` — total wall-clock time in nanoseconds. On CPU, scales with `eval_count`.
- Observation 4 shows that `eval_count` is capped at `num_predict`, confirming the autoregressive loop terminates on the budget limit.

---

## Concepts verified

- [ ] `prompt_eval_count` is identical across all runs for the same input — observable at Observation 3
- [ ] `eval_count` never exceeds `num_predict` — observable at Observation 4
- [ ] `total_duration` scales with `eval_count` on CPU inference — observable at Observation 2

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_output_token_scaling()`, add `1` to the limits list: `for limit in (1, 8, 32, 128)`
- **Expected degradation:**
  - `eval_count=1` for `num_predict=1` regardless of prompt — the autoregressive loop stops after a single token
  - The response is always a single token fragment, never a complete answer
  - Shows that `num_predict` is a hard ceiling, not a target: the loop stops as soon as it is reached, even mid-sentence

Restore the original limits list after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | LLM inference server — exposes the transformer and autoregressive loop via HTTP |
