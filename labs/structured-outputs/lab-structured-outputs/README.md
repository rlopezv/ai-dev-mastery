---
id: "lab-structured-outputs"
title: "Structured Outputs"
type: "lab-readme"
step: "structured-outputs"
path: "labs/structured-outputs/lab-structured-outputs/README.md"
status: "draft"
level: "intermediate"
concepts:
  - "structured-outputs"
  - "json-mode"
  - "schema-enforcement"
prerequisites:
  - "docs/structured-outputs/structured-outputs.md"
related:
  - "docs/structured-outputs/README.md"
summary: "Implementation lab — compares prompt-only JSON, JSON mode, and Pydantic schema enforcement on adversarial inputs, demonstrating that only schema enforcement guarantees typed objects with zero parse failures."
---

# Structured Outputs
## Navigation

[Labs](../../README.md) / [Structured Outputs — Labs](../README.md) / Structured Outputs

---

**Module:** `structured-outputs`
**Type:** implementation
**Doc:** `docs/structured-outputs/structured-outputs.md`
**Required:** yes

## What this lab demonstrates

- Observation 1: prompt-only JSON format instruction — shows parse failures on adversarial inputs
- Observation 2: JSON mode enabled — syntactic validity guaranteed, shape still model-determined
- Observation 3: Pydantic schema enforcement — `message.parsed` returns a typed `ReviewSummary` object with zero parse failures

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/structured-outputs/requirements.txt`

## Run

```bash
cd labs/structured-outputs
python lab-structured-outputs/main.py
```

## Expected output

```
=== Observation 1: Prompt-only JSON ===
Input 1: "Great product, fast delivery!"
  raw: {"sentiment": "positive", "score": 5, "key_issues": []}
  parsed: OK
Input 2: "The item was okay but shipping took forever and packaging was damaged."
  raw: I'd classify this review as neutral...{"sentiment": "neutral"...}
  parsed: FAIL — extra prose before JSON
...
Prompt-only parse success: 3/5

=== Observation 2: JSON mode ===
Input 1: {"sentiment": "positive", "score": 5, "key_issues": []}
  valid JSON: yes | conforms to schema: unknown (no enforcement)
...
JSON mode parse success: 5/5 | Schema compliance: manual check required

=== Observation 3: Schema enforcement (Pydantic) ===
Input 1: ReviewSummary(sentiment='positive', score=5, key_issues=[])
Input 2: ReviewSummary(sentiment='neutral', score=3, key_issues=['slow shipping', 'damaged packaging'])
...
Schema enforcement parse success: 5/5
All typed objects. No manual json.loads needed.
```

## What to observe

- **Observation 1:** simple inputs may parse successfully, but adversarial inputs (long text, special characters) produce prose before the JSON block — the extraction logic fails or requires a heuristic `find("{")` workaround
- **Observation 2:** JSON mode returns HTTP 200 with valid JSON every time — but `schema_compliant` count may be lower than `parse_success`, showing that syntactic enforcement does not imply structural conformance
- **Observation 3:** all 5 inputs return typed `ReviewSummary` objects — `sentiment` is always one of the three allowed values, `score` is always 1–5; no manual `json.loads` needed

## Concepts verified

- [ ] Prompt-only JSON fails on adversarial inputs (long text, special characters)
- [ ] JSON mode guarantees syntactic validity but not structural conformance
- [ ] Pydantic schema enforcement returns a typed object from `message.parsed` with zero failures
- [ ] `sentiment` is always one of `["positive", "neutral", "negative"]`; `score` is always 1–5

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `ReviewSummary`, remove the `Literal` type from `sentiment` and replace it with `str`
- **Expected degradation:**
  - Pydantic still returns a parsed object — parse success stays 5/5
  - `sentiment` may contain non-standard values such as `"mixed"`, `"somewhat negative"`, or `"mostly positive"`
  - Vocabulary bounds are lost: the schema no longer enforces the three-way classification
  - Evaluation code comparing against `"positive"/"neutral"/"negative"` would fail despite correct classification

Restore `Literal["positive", "neutral", "negative"]` after the experiment.
