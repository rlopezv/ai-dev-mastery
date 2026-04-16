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

## What to observe

- **Observation 1 vs 2:** count unique responses — the complete prompt produces the fewest. Format specification is the gating factor, not the system prompt or instruction.
- **Observation 2:** responses vary in format (single word, full sentence, explanation) even for the same input. The model is not wrong — it simply has no format constraint.
- **Observation 3:** without an explicit instruction, some runs classify, others describe. The model infers the task from context — sometimes correctly, sometimes not.

---

## Concepts verified

- [ ] Format specification is the component most responsible for output consistency
- [ ] Without instruction, the model may classify or describe — behavior is undefined
- [ ] System prompt affects tone and conciseness, not classification accuracy

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `build_complete_prompt()`, remove the enumerated options from the format spec — change `"Respond with one word only: positive, negative, or neutral."` to `"Respond with one word only."`
- **Expected degradation:**
  - Model invents its own category labels ("mixed", "ambivalent", "critical")
  - Unique response count increases even for Observation 1
  - Shows that format spec must enumerate the valid outputs — open-ended instructions allow vocabulary drift

Restore the original format spec after the experiment.
