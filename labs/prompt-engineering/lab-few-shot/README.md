---
id: "lab-few-shot"
title: "Few-Shot Prompting"
type: "lab-readme"
step: "prompt-engineering"
path: "labs/prompt-engineering/lab-few-shot/README.md"
status: "draft"
level: "foundational"
concepts:
  - "few-shot-prompting"
  - "in-context-learning"
prerequisites:
  - "docs/prompt-engineering/few-shot.md"
related:
  - "docs/prompt-engineering/README.md"
summary: "Implementation lab — measures accuracy improvement from zero-shot to three-shot on topic classification, and demonstrates how examples anchor output format."
---

# Few-Shot Prompting

## Navigation

[Labs](../../README.md) / [Prompt Engineering — Labs](../README.md) / Few-Shot Prompting

---

## Overview

This lab builds a topic classifier using labeled examples in the prompt. It runs the same test set in zero-shot, one-shot, and three-shot configurations and compares accuracy across the three modes, making the accuracy benefit of few-shot prompting directly measurable.

**Out of scope:** chain-of-thought reasoning (covered in `lab-chain-of-thought`), reusable pattern templates (covered in `lab-prompt-patterns`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `few-shot-prompting` | `classify(examples, target)` — the shot count is the length of `examples`; zero-shot passes an empty list |
| `in-context-learning` | `evaluate(shot_count)` — the model infers the classification pattern from examples rather than from explicit task instructions |

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
python lab-few-shot/main.py
```

---

## Expected Output

```
=== Few-Shot Prompting — Topic Classification ===
Test set: 8 items   Classes: economics, sports, technology, or politics

--- Zero-shot (0 examples) ---
  ✓  expected=economics     got='economics'
  ✗  expected=sports        got='The text is about...'
  ...
Accuracy: 5/8 = 63%

--- One-shot  (1 example)  ---
  ...
Accuracy: 6/8 = 75%

--- Few-shot  (3 examples) ---
  ...
Accuracy: 7/8 = 88%
```

---

## What to observe

- **Zero-shot vs few-shot:** compare accuracy scores across the three runs. The gap is most visible on ambiguous inputs (e.g., a text that could be economics or politics).
- **Format anchoring:** zero-shot may return full sentences; few-shot anchors the output to a single-word label because the examples show that format. The normalization in `evaluate()` partially compensates, but not for all variations.
- **Class distribution:** with 3 examples from 4 classes, coverage is uneven. Note whether the under-represented class has lower accuracy.

---

## Concepts verified

- [ ] Accuracy improves with shot count, especially on ambiguous inputs — observable by comparing accuracy scores across modes
- [ ] Examples anchor the output to a single-word label format — observable at zero-shot vs few-shot output format
- [ ] Label leakage is visible if all examples share the same class — observable at Failure case

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `EXAMPLES`, change some labels to use inconsistent casing — replace `"economics"` with `"Economics"` and `"sports"` with `"Sports"` in 2–3 of the examples
- **Expected degradation:**
  - The model mirrors the inconsistent casing from examples: some outputs are `"Economics"`, others `"economics"`
  - `predicted == expected` fails for outputs with capitalized labels despite correct classification
  - Accuracy drops even though the model is semantically correct — the label format drift causes evaluation failures

Restore lowercase labels in `EXAMPLES` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves the classification requests via the OpenAI-compatible endpoint |
