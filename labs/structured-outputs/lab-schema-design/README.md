---
id: "lab-schema-design"
title: "Schema Design"
type: "lab-readme"
step: "structured-outputs"
path: "labs/structured-outputs/lab-schema-design/README.md"
status: "draft"
level: "intermediate"
concepts:
  - "schema-design"
  - "schema-enforcement"
prerequisites:
  - "docs/structured-outputs/schema-design.md"
related:
  - "docs/structured-outputs/README.md"
summary: "Implementation lab — compares unconstrained vs constrained Pydantic schemas on adversarial inputs, measuring enum violations and hallucinated optional fields to demonstrate the impact of schema constraints."
---

# Schema Design

## Navigation

[Labs](../../README.md) / [Structured Outputs — Labs](../README.md) / Schema Design

---

## Overview

This lab runs 10 test inputs (including adversarial cases with missing or ambiguous data) through two Pydantic schemas — one unconstrained with plain `str` fields, one constrained with `Literal`, bounded `int`, and optional nullable fields — and measures enum violations and hallucinated optional field values for each.

**Out of scope:** JSON mode vs schema enforcement comparison (covered in `lab-structured-outputs`), tool declaration and execution (covered in `lab-tool-usage`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `schema-design` | `ContactConstrained` Pydantic model — field selection, `Literal` enum, `str \| None = None` optional, `Field(max_length=...)` constraint applied to each field |
| `schema-enforcement` | Both schemas use `client.beta.chat.completions.parse(response_format=...)` — the constrained schema enforces tighter bounds that eliminate enum violations and force `None` on absent fields |

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
python lab-schema-design/main.py
```

---

## Expected Output

```
=== Schema comparison: ContactExtraction ===

--- Unconstrained schema ---
Input 1 "Email John at john@co.com": name='John', email='john@co.com', role='unknown'  ✓
Input 2 "Call the office at 555-1234": name='', email=None, phone='555-1234', role='unknown'
  role: 'unknown' ← correct default
Input 5 "Reach out to the team" (no contact info):
  name='Team' ← hallucinated | email='contact@company.com' ← hallucinated
Unconstrained — parse success: 10/10 | enum violations: 3 | hallucinated optionals: 4

--- Constrained schema ---
Input 5 "Reach out to the team":
  name='Team', email=None, phone=None  ← optional fields return None, not hallucinated
Constrained — parse success: 10/10 | enum violations: 0 | hallucinated optionals: 0

=== Summary ===
  Unconstrained schema: 10/10 parses, 3 enum violations, 4 hallucinated optional fields
  Constrained schema:   10/10 parses, 0 enum violations, 0 hallucinated optional fields
  Conclusion: constraints eliminate enum violations and force None on absent optional fields
```

---

## What to observe

- **Unconstrained:** parse success is 10/10, but `enum_violations > 0` and `hallucinated_optionals > 0` — especially on adversarial inputs with no contact info (inputs 4–5); the model guesses values for absent fields.
- **Constrained:** `enum_violations` drops to 0; optional fields return `None` instead of fabricated values — the schema shape enforces `None` even when the model would otherwise fill in a guess.

---

## Concepts verified

- [ ] `Literal` maps enum to JSON Schema `enum` — eliminates out-of-vocabulary values — observable at enum violations count
- [ ] `str | None = None` returns `None` instead of a hallucinated value when field is absent — observable at hallucinated optionals count
- [ ] `Field(max_length=...)` bounds string length — observable at title field length in output
- [ ] Constraints do not degrade parse success rate — both schemas succeed equally on parseable inputs — observable at parse success row

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `ContactConstrained`, change `role: Literal["engineer", "manager", "executive", "unknown"] = "unknown"` to `role: str | None = None`
- **Expected degradation:**
  - `enum_violations` stays 0 — there is no enum to violate
  - Non-standard values such as `"director"`, `"developer"`, or `"CEO"` pass through unchecked
  - The `enum_violations` metric becomes meaningless as a comparison signal

Restore the `Literal` type on `role` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves schema comparison requests via the OpenAI-compatible endpoint with Pydantic `response_format` |
