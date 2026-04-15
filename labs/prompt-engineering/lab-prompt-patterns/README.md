# lab-prompt-patterns

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

## Concepts verified

- Role prompt produces domain vocabulary without explicit content instructions
- Format pattern produces parseable JSON on standard inputs
- Step pattern labels all four sections including "None identified." for empty ones
- Benchmark harness reports accuracy as correct/total with failure details
