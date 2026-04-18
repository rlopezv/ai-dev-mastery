---
id: "lab-prompt-patterns"
title: "Prompt Patterns"
type: "lab-readme"
step: "prompt-engineering"
path: "labs/prompt-engineering/lab-prompt-patterns/README.md"
status: "draft"
level: "foundational"
concepts:
  - "prompt-patterns"
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

**Module:** `prompt-engineering`
**Type:** implementation
**Doc:** `docs/prompt-engineering/prompt-patterns.md`
**Required:** yes

## What this lab demonstrates

- Role prompting: domain-appropriate vocabulary and constraint adherence
- Output format specification: JSON structure compliance and benchmark accuracy
- Step-by-step instruction: all labeled steps present in code review output
- Benchmark harness: accuracy measurement across a fixed test set

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/prompt-engineering/requirements.txt`

## Run

```bash
cd labs/prompt-engineering
python lab-prompt-patterns/main.py
```

## Expected output

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

## What to observe

- **Pattern 1:** the role prompt shapes vocabulary without instructing content. Notice technical terms and trade-off framing appear without being requested explicitly.
- **Pattern 2:** `check_format()` passes only when JSON is valid AND `sentiment` matches the expected label. A well-formed JSON with wrong sentiment is still a failure.
- **Pattern 3:** all four step labels appear in order. `check_steps_present()` confirms presence but not order — read the response to verify sequencing.

---

## Concepts verified

- [ ] Role prompt produces domain vocabulary without explicit content instructions
- [ ] Format pattern produces parseable JSON on standard inputs
- [ ] Step pattern labels all four sections including "None identified." for empty ones
- [ ] Benchmark harness reports accuracy as correct/total with failure details

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `build_steps_prompt()`, reorder the step numbers in the prompt to 1, 3, 2, 4
- **Expected degradation:**
  - `check_steps_present()` still returns `True` — all four labels appear
  - But the content is scrambled: correctness issues appear under "Step 3", performance under "Step 2"
  - Shows that explicit numbering enforces section identity but not section order — the model follows the numbers, not the intended sequence

Restore the original step order (1, 2, 3, 4) after the experiment.
