---
id: "lab-prompt-patterns"
title: "Prompt Patterns"
type: "lab-readme"
step: "prompt-engineering"
path: "labs/prompt-engineering/lab-prompt-patterns/README.md"
status: "draft"
level: "foundational"
concepts:
  - "prompt-pattern"
  - "role-prompting"
  - "output-format-specification"
prerequisites:
  - "docs/prompt-engineering/prompt-patterns.md"
related:
  - "docs/prompt-engineering/README.md"
summary: "Implementation lab — benchmarks role prompting, output format specification, and step-by-step instruction patterns with measurable accuracy and compliance checks."
---

# Prompt Patterns

## Navigation

[Labs](../../README.md) / [Prompt Engineering — Labs](../README.md) / Prompt Patterns

---

## Overview

This lab implements three reusable prompt pattern templates as Python functions and tests each against a fixed input set. It includes a benchmark harness that reports format compliance and content accuracy, making pattern performance directly measurable.

**Out of scope:** combining patterns with few-shot examples (covered in `lab-few-shot`), chain-of-thought answer extraction (covered in `lab-chain-of-thought`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `prompt-pattern` | All three observations — each implements one pattern as a template function with typed parameters |
| `role-prompting` | `build_role_prompt(role, domain, tone, constraint, task)` — the role anchors vocabulary and constraints without specifying content |
| `output-format-specification` | `build_format_prompt(schema, input_text)` — JSON schema and compliance instruction appended to constrain response structure |

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
python lab-prompt-patterns/main.py
```

---

## Expected Output

```
=== Pattern 1: Role prompting ===
Response:
  Synchronous REST calls introduce several risks in microservice architectures...
  [technical vocabulary, trade-off focused response]

=== Pattern 2: Output format specification ===
[format-spec] Accuracy: 4/5 = 80%

=== Pattern 3: Step-by-step instruction ===
Response:
  Step 1: The code defines a divide function...
  Step 2: Division by zero — divide(10, 0) will raise ZeroDivisionError...
  Step 3: None identified.
  Step 4: request-changes

All steps labeled: ✓
```

---

## What to observe

- **Pattern 1:** the role prompt shapes vocabulary without instructing content. Notice technical terms and trade-off framing appear without being requested explicitly.
- **Pattern 2:** `check_format()` passes only when JSON is valid AND `sentiment` matches the expected label. A well-formed JSON with a wrong sentiment value is still a failure.
- **Pattern 3:** all four step labels appear in order. `check_steps_present()` confirms presence but not order — read the response to verify sequencing.

---

## Concepts verified

- [ ] Role prompt produces domain vocabulary without explicit content instructions — observable at Pattern 1 response
- [ ] Format pattern produces parseable JSON on standard inputs — observable at Pattern 2 accuracy
- [ ] Step pattern labels all four sections including "None identified." for empty ones — observable at Pattern 3 response
- [ ] Benchmark harness reports accuracy as correct/total with failure details — observable at Pattern 2 output

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `build_steps_prompt()`, reorder the step numbers in the prompt to 1, 3, 2, 4
- **Expected degradation:**
  - `check_steps_present()` still returns `True` — all four labels appear
  - But the content is scrambled: correctness issues appear under "Step 3", performance under "Step 2"
  - Shows that explicit numbering enforces section identity but not section order — the model follows the numbers, not the intended sequence

Restore the original step order (1, 2, 3, 4) after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves pattern evaluation requests via the OpenAI-compatible endpoint |
