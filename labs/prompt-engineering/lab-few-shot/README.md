# lab-few-shot

**Module:** `prompt-engineering`
**Type:** implementation
**Doc:** `docs/prompt-engineering/few-shot.md`
**Required:** yes

## What this lab demonstrates

- Zero-shot vs one-shot vs three-shot accuracy on topic classification
- Consistent output format enforced by example labels
- Accuracy improvement as shot count increases

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/prompt-engineering/requirements.txt`

## Run

```bash
cd labs/prompt-engineering
python lab-few-shot/main.py
```

## Expected output

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

## What to observe

- **Zero-shot vs few-shot:** compare accuracy scores across the three runs. The gap is most visible on ambiguous inputs (e.g., a text that could be economics or politics).
- **Format anchoring:** zero-shot may return full sentences; few-shot anchors the output to a single-word label because the examples show that format. The normalization in `evaluate()` partially compensates, but not for all variations.
- **Class distribution:** with 3 examples from 4 classes, coverage is uneven. Note whether the under-represented class has lower accuracy.

---

## Concepts verified

- [ ] Accuracy improves with shot count, especially on ambiguous inputs
- [ ] Examples anchor the output to a single-word label format
- [ ] Label leakage is visible if all examples share the same class

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `EXAMPLES`, change some labels to use inconsistent casing — replace `"economics"` with `"Economics"` and `"sports"` with `"Sports"` in 2–3 of the examples
- **Expected degradation:**
  - The model mirrors the inconsistent casing from examples: some outputs are `"Economics"`, others `"economics"`
  - `predicted == expected` fails for outputs with capitalized labels despite correct classification
  - Accuracy drops even though the model is semantically correct — the label format drift causes evaluation failures

Restore lowercase labels in `EXAMPLES` after the experiment.
