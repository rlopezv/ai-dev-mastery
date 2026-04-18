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

**Module:** llm-fundamentals  
**Type:** observation  
**Doc:** `docs/llm-fundamentals/llm-architecture.md`

---

## What this lab demonstrates

This lab makes the transformer inference pipeline observable through the Ollama API. It shows that behind the simple "send a prompt, get a response" interface, the API reports detailed telemetry that maps directly to pipeline stages.

**Observations:**
1. What models are available and their metadata
2. How a generation request maps to input/output token counts and timing
3. That `prompt_eval_count` is deterministic for a fixed input
4. That `eval_count` is bounded by `num_predict`

---

## How to run

```bash
# From the labs/llm-fundamentals/ directory:
python lab-llm-anatomy/main.py
```

**Prerequisites:** Ollama running with `llama3.2` loaded. See the module README for setup.

---

## Expected output

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

- `prompt_eval_count` — number of input tokens processed. Should be consistent across runs for the same prompt.
- `eval_count` — number of output tokens generated. Should not exceed `num_predict`.
- `total_duration` — total wall-clock time in nanoseconds. On CPU, this scales with `eval_count`.
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

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `MODEL` | `llama3.2` | Model to use |
| `NUM_PREDICT` | `128` | Maximum output tokens per request |
