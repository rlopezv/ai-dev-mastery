---
id: "lab-inference-parameters"
title: "Inference Parameters"
type: "lab-readme"
step: "llm-fundamentals"
path: "labs/llm-fundamentals/lab-inference-parameters/README.md"
status: "draft"
level: "foundational"
concepts:
  - "inference-parameters"
  - "temperature"
  - "top-k-sampling"
  - "top-p-sampling"
prerequisites:
  - "docs/llm-fundamentals/inference-parameters.md"
related:
  - "docs/llm-fundamentals/README.md"
summary: "Observation lab — isolates the effect of temperature, top-k, and top-p by running the same prompt with systematically varied parameters and comparing outputs."
---

# Inference Parameters

## Navigation

[Labs](../../README.md) / [LLM Fundamentals — Labs](../README.md) / Inference Parameters

---

## Overview

This lab runs the same prompts with systematically varied inference parameters and prints outputs side by side. It makes the sampling controls tangible: temperature, top-k, and top-p each produce measurably different outputs on the same model with the same input.

**Out of scope:** `repeat_penalty`, `seed`, provider-specific parameters beyond Ollama.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `inference-parameters` | `generate()` — `options` block passed to Ollama API on every call |
| `temperature` | `observe_determinism()` / `observe_variance()` — controls width of the sampling distribution |
| `top-k-sampling` | `observe_top_k()` — restricts candidate pool to the k highest-probability tokens |
| `top-p-sampling` | `observe_top_p()` — restricts candidate pool by cumulative probability threshold |

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
python lab-inference-parameters/main.py
```

---

## Expected Output

```
Model: llama3.2 | num_predict: 64 | runs per observation: 3

=== Observation 1: Determinism at temperature=0 ===
Prompt: 'Once upon a time in a futuristic city,'

  Run 1: 'there existed a society where technology...'
  Run 2: 'there existed a society where technology...'
  Run 3: 'there existed a society where technology...'

  ✓ All 3 runs produced identical output

=== Observation 2: Variance at temperature=1.0 ===
Prompt: 'Once upon a time in a futuristic city,'

  Run 1: 'where towering skyscrapers...'
  Run 2: 'the streets hummed with electric...'
  Run 3: 'a young engineer named Aria...'

  Unique responses: 3 / 3
  ✓ Output varies as expected at temperature=1.0

=== Observation 3: top_k effect ===
  top_k=1    → 'there existed a society...'   (identical to greedy)
  top_k=10   → 'a city powered by...'
  top_k=100  → 'where neon lights...'

=== Observation 4: top_p effect ===
  top_p=0.1  → 'there existed a society...'   (narrow pool — near-greedy)
  top_p=0.5  → 'where the lights...'
  top_p=0.95 → 'a sprawling metropolis...'

=== Observation 5: Temperature on a factual prompt ===
Prompt: 'The capital of Japan is'

  temperature=0.0 → 'Tokyo.'
  temperature=0.7 → 'Tokyo.'
  temperature=1.5 → 'Kyoto.'    ← higher temperature → wrong token selected
```

---

## What to observe

- **Observation 1 vs 2:** Same model, same prompt, same `num_predict` — only temperature differs. This isolates the parameter's effect from all other variables.
- **Observation 3:** `top_k=1` forces greedy decoding regardless of temperature. It behaves identically to temperature=0 because only one token is eligible for sampling.
- **Observation 4:** Low `top_p` produces near-deterministic output by restricting the pool to the few most probable tokens; high `top_p` allows broader variance. Compare with Observation 3 — both narrow the pool, but top_p adapts to the distribution shape while top_k uses a fixed count.
- **Observation 5:** Higher temperature on a factual prompt does not improve the answer — it increases the probability of selecting a wrong but plausible token. Low temperature is correct for tasks with a single right answer.

---

## Concepts verified

- [ ] temperature=0 produces identical output across all runs — observable at Observation 1
- [ ] temperature=1.0 produces different output across runs — observable at Observation 2
- [ ] top_k=1 is equivalent to greedy decoding at any temperature — observable at Observation 3
- [ ] Low top_p produces near-deterministic output; high top_p allows variance — observable at Observation 4
- [ ] High temperature increases wrong-token selection on factual prompts — observable at Observation 5

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_determinism()`, change `temperature=0.0` to `temperature=0.1`
- **Expected degradation:**
  - The `✓ All 3 runs produced identical output` check fails
  - Outputs vary across runs even at low temperature, showing that only exactly `0.0` guarantees determinism — any positive value reintroduces sampling

Restore `temperature=0.0` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | LLM inference server — accepts `options.temperature`, `options.top_k`, `options.top_p` per request |
