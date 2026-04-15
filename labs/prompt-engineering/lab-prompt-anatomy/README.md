# lab-prompt-anatomy

**Module:** `prompt-engineering`
**Type:** observation
**Doc:** `docs/prompt-engineering/prompt-anatomy.md`
**Required:** yes

## What this lab demonstrates

- Complete prompt (all 5 components) produces consistent output
- Removing output format specification increases response variation
- Removing instruction causes off-task responses
- Removing system prompt changes behavioral register

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/prompt-engineering/requirements.txt`

## Run

```bash
cd labs/prompt-engineering
python lab-prompt-anatomy/main.py
```

## Expected output

```
=== Observation 1: Complete prompt (all components) ===
  Run 1: 'negative'
  Run 2: 'negative'
  ...
  Unique responses: 1 / 5  → ['negative']

=== Observation 2: No output format specification ===
  Run 1: 'The sentiment is mixed — negative toward the migration guide...'
  Run 2: 'negative'
  ...
  Unique responses: 3 / 5  → [...]

=== Observation 3: No instruction ===
  Run 1: 'neutral'
  Run 2: 'The text describes a framework...'
  ...

=== Observation 4: No system prompt ===
  Run 1: 'negative'
  ...
```

## Concepts verified

- Format specification is the component most responsible for output consistency
- Without instruction, the model may classify or describe — behavior is undefined
- System prompt affects tone and conciseness, not classification accuracy
