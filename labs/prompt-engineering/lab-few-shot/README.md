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

## Concepts verified

- Accuracy improves with shot count, especially on ambiguous inputs
- Examples anchor the output to a single-word label format
- Label leakage is visible if all examples share the same class
