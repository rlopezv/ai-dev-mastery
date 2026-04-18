---
id: "lab-prompt-anatomy"
title: "Prompt Anatomy"
type: "lab-readme"
step: "prompt-engineering"
path: "labs/prompt-engineering/lab-prompt-anatomy/README.md"
status: "draft"
level: "foundational"
concepts:
  - "prompt-anatomy"
  - "output-format-specification"
  - "system-prompt"
prerequisites:
  - "docs/prompt-engineering/prompt-anatomy.md"
related:
  - "docs/prompt-engineering/README.md"
summary: "Observation lab — isolates the effect of each prompt component by removing them one at a time and measuring output consistency across repeated runs."
---

# Prompt Anatomy

## Navigation

[Labs](../../README.md) / [Prompt Engineering — Labs](../README.md) / Prompt Anatomy

---

## Overview

This lab systematically removes one prompt component at a time from an otherwise complete sentiment classification prompt and runs each configuration five times. It makes the contribution of each component directly observable by comparing unique response counts across runs.

**Out of scope:** few-shot examples (covered in `lab-few-shot`), chain-of-thought (covered in `lab-chain-of-thought`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `prompt-anatomy` | All four observations — each removes one of the five components to isolate its effect |
| `output-format-specification` | `observe_no_format()` — removed to show that format specification is the primary driver of output consistency |
| `system-prompt` | `observe_no_system()` — removed to show the effect on behavioral register and tone |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# Install dependencies (from the module root):
pip install -r labs/prompt-engineering/requirements.txt
```

---

## Run

```bash
cd labs/prompt-engineering
python lab-prompt-anatomy/main.py
```

---

## Expected Output

```
=== Observation 1: Complete prompt (all components) ===
  Run 1: 'negative'
  Run 2: 'negative'
  Run 3: 'negative'
  Run 4: 'negative'
  Run 5: 'negative'
  Unique responses: 1 / 5  → ['negative']

=== Observation 2: No output format specification ===
  Run 1: 'The sentiment is mixed — negative toward the migration guide...'
  Run 2: 'negative'
  Run 3: 'I would classify this as negative.'
  ...
  Unique responses: 3 / 5  → [...]

=== Observation 3: No instruction ===
  Run 1: 'neutral'
  Run 2: 'The text describes a framework migration issue with some frustration...'
  ...
  Unique responses: 2 / 5

=== Observation 4: No system prompt ===
  Run 1: 'negative'
  Run 2: 'negative'
  ...
  Unique responses: 1 / 5
```

---

## What to observe

- **Observation 1 vs 2:** count unique responses — the complete prompt produces the fewest. Format specification is the gating factor for consistency, not the system prompt or instruction.
- **Observation 2:** responses vary in format (single word, full sentence, explanation) even for the same input. The model is not wrong — it simply has no format constraint.
- **Observation 3:** without an explicit instruction, some runs classify, others describe. The model infers the task from context — sometimes correctly, sometimes not.

---

## Concepts verified

- [ ] Format specification is the component most responsible for output consistency — observable at Observation 1 vs 2
- [ ] Without instruction, the model may classify or describe — behavior is undefined — observable at Observation 3
- [ ] System prompt affects tone and conciseness, not classification accuracy — observable at Observation 4

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `build_complete_prompt()`, remove the enumerated options from the format spec — change `"Respond with one word only: positive, negative, or neutral."` to `"Respond with one word only."`
- **Expected degradation:**
  - Model invents its own category labels ("mixed", "ambivalent", "critical")
  - Unique response count increases even for Observation 1
  - Shows that format spec must enumerate the valid outputs — open-ended instructions allow vocabulary drift

Restore the original format spec after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves the classification requests via the OpenAI-compatible endpoint |
