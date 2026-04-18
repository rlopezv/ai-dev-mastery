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
  - "top-k"
  - "top-p"
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

**Module:** llm-fundamentals  
**Type:** observation  
**Doc:** `docs/llm-fundamentals/inference-parameters.md`

---

## What this lab demonstrates

This lab runs the same prompts with systematically varied inference parameters and prints the outputs side by side. It makes the sampling controls tangible: temperature, top-k, and top-p each produce measurably different outputs on the same model with the same input.

**Observations:**
1. temperature=0 produces deterministic output across repeated runs
2. temperature=1.0 produces output variance across repeated runs
3. top_k restricts the candidate pool (top_k=1 is greedy decoding)
4. top_p restricts by cumulative probability (low top_p → narrow pool)
5. Temperature does not improve accuracy on factual prompts

---

## How to run

```bash
# From the labs/llm-fundamentals/ directory:
python lab-inference-parameters/main.py
```

**Prerequisites:** Ollama running with `llama3.2` loaded. See the module README for setup.

---

## Expected output

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

=== Observation 5: Temperature on a factual prompt ===
Prompt: 'The capital of Japan is'

  temperature=0.0 → 'Tokyo.'
  temperature=0.7 → 'Tokyo.'
  temperature=1.5 → 'Kyoto.'    ← higher temperature → wrong token selected
```

---

## What to observe

- **Observation 1 vs 2:** The same model, same prompt, same `num_predict` — only temperature differs. This isolates the sampling parameter's effect from all other variables.
- **Observation 3:** `top_k=1` forces greedy decoding regardless of temperature. It behaves identically to temperature=0 because only one token is eligible for sampling.
- **Observation 5:** Higher temperature on a factual prompt does not improve the answer — it increases the probability of selecting a wrong but plausible token. Low temperature is correct for tasks with a single right answer.

---

## Concepts verified

- [ ] temperature=0 produces identical output across all runs — observable at Observation 1
- [ ] temperature=1.0 produces different output across runs — observable at Observation 2
- [ ] top_k=1 is equivalent to greedy decoding at any temperature — observable at Observation 3
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

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `MODEL` | `llama3.2` | Model to use |
| `NUM_PREDICT` | `64` | Maximum output tokens per request |
