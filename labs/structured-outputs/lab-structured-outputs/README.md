---
id: "lab-structured-outputs"
title: "Structured Outputs"
type: "lab-readme"
step: "structured-outputs"
path: "labs/structured-outputs/lab-structured-outputs/README.md"
status: "draft"
level: "intermediate"
concepts:
  - "structured-output"
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

## Overview

This lab runs five adversarial inputs through three successive approaches to structured model output — prompt-only JSON format instruction, JSON mode, and Pydantic schema enforcement — and compares parse success and schema compliance across all three. It makes the reliability difference between approaches directly measurable.

**Out of scope:** tool use (covered in `lab-tool-usage`), schema constraint design (covered in `lab-schema-design`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `structured-output` | `observe_schema_enforcement()` — `client.beta.chat.completions.parse(response_format=ReviewSummary)` returns a typed `ReviewSummary` instance; `message.parsed` is the entry point |
| `json-mode` | `observe_json_mode()` — `response_format={"type": "json_object"}` guarantees syntactically valid JSON but not structural conformance |
| `schema-enforcement` | `observe_schema_enforcement()` — API enforces the declared schema before returning; `sentiment` is always one of three allowed values; `score` is always 1–5 |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# Install dependencies (from the module root):
pip install -r labs/structured-outputs/requirements.txt
```

---

## Run

```bash
cd labs/structured-outputs
python lab-structured-outputs/main.py
```

---

## Expected Output

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

---

## What to observe

- **Observation 1:** simple inputs may parse successfully, but adversarial inputs (long text, special characters) produce prose before the JSON block — extraction fails or requires a heuristic `find("{")` workaround.
- **Observation 2:** JSON mode returns HTTP 200 with valid JSON every time — but `schema_compliant` count may be lower than `parse_success`, showing that syntactic enforcement does not imply structural conformance.
- **Observation 3:** all 5 inputs return typed `ReviewSummary` objects — `sentiment` is always one of the three allowed values, `score` is always 1–5; no manual `json.loads` needed.

---

## Concepts verified

- [ ] Prompt-only JSON fails on adversarial inputs — observable at Observation 1 parse success rate
- [ ] JSON mode guarantees syntactic validity but not structural conformance — observable at Observation 2 schema compliance vs parse success
- [ ] Schema enforcement returns a typed object from `message.parsed` with zero failures — observable at Observation 3
- [ ] `sentiment` is always one of `["positive", "neutral", "negative"]`; `score` is always 1–5 — observable at Observation 3 output

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

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves structured output requests via the OpenAI-compatible `/beta/chat/completions` endpoint with `response_format` support |
