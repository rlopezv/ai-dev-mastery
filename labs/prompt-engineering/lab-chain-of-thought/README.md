---
id: "lab-chain-of-thought"
title: "Chain of Thought"
type: "lab-readme"
step: "prompt-engineering"
path: "labs/prompt-engineering/lab-chain-of-thought/README.md"
status: "draft"
level: "foundational"
concepts:
  - "chain-of-thought"
  - "answer-extraction"
prerequisites:
  - "docs/prompt-engineering/chain-of-thought.md"
related:
  - "docs/prompt-engineering/README.md"
summary: "Implementation lab — compares direct vs chain-of-thought accuracy on multi-step word problems and demonstrates answer extraction via a structured marker."
---

# Chain of Thought

## Navigation

[Labs](../../README.md) / [Prompt Engineering — Labs](../README.md) / Chain of Thought

---

## Overview

This lab runs a fixed set of multi-step word problems in two modes — direct answer and chain-of-thought — and compares correct counts. It also demonstrates the `"Answer:"` marker extraction pattern, making CoT answer parsing a concrete, testable operation.

**Out of scope:** few-shot chain-of-thought with full reasoning examples (concept-only in `chain-of-thought.md`), reusable pattern templates (covered in `lab-prompt-patterns`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `chain-of-thought` | `solve_cot(problem)` — appends `"Let's think step by step. At the end, state your final answer on a new line starting with 'Answer:'"` to trigger reasoning before the answer |
| `answer-extraction` | `parse_cot_answer(response_text)` — splits on `COT_MARKER = "Answer:"` to isolate the final answer from the reasoning trace |

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
python lab-chain-of-thought/main.py
```

---

## Expected Output

```
=== Chain-of-Thought vs Direct Answering ===

--- Problem 1 ---
  Problem: A warehouse has 240 boxes...
  Direct  → '105'  (normalized: 105)  ✓
  CoT     → extracted: '105'  (normalized: 105)  ✓
  Expected: 105

--- Problem 2 ---
  Problem: Alice is twice as old as Bob...
  Direct  → '13'  (normalized: 13)  ✗
  CoT     → extracted: '26'  (normalized: 26)  ✓
  Expected: 26

--- Problem 3 ---
  Problem: ...
  Direct  → ...  ✗
  CoT     → ...  ✓
  Expected: ...

Results:  Direct 1/3   CoT 3/3
```

---

## What to observe

- **Direct vs CoT:** compare correct counts — CoT should match or exceed direct on all three problems. Problems 2 and 3 are where CoT provides the largest benefit.
- **Reasoning trace:** read the CoT output before `"Answer:"` — confirm the model is actually computing intermediate steps, not guessing.
- **Marker extraction:** if the model omits `"Answer:"`, `parse_cot_answer` raises `ValueError` and the problem is counted as wrong. This makes extraction reliability directly visible.

---

## Concepts verified

- [ ] CoT correct count ≥ direct correct count on multi-step problems — observable at Results line
- [ ] `"Answer:"` marker is present in every CoT response — observable in individual problem output
- [ ] `parse_cot_answer` returns clean numeric answer without reasoning trace — observable at "extracted:" values

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** change `COT_MARKER = "Answer:"` to `COT_MARKER = "ANSWER:"`
- **Expected degradation:**
  - `parse_cot_answer` raises `ValueError` for every problem — the model writes `"Answer:"` (mixed case), not `"ANSWER:"`
  - CoT correct count drops to 0; all problems are counted as parse failures
  - Shows that extraction markers must match the exact case the model produces — the prompt drives the format, not the extractor

Restore `COT_MARKER = "Answer:"` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves the word problem requests via the OpenAI-compatible endpoint |
