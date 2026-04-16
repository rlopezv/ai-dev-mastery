# lab-schema-design

**Module:** `structured-outputs`
**Type:** implementation
**Doc:** `docs/structured-outputs/schema-design.md`
**Required:** optional

## What this lab demonstrates

- Side-by-side comparison of unconstrained vs constrained Pydantic schemas on the same test set
- Constrained schema uses: `Literal` (enum), `int` with bounds, `str | None` with default, `list[str]`
- Adversarial inputs: missing fields, unusual formats, multilingual text, very short text
- Accuracy metrics: parse success rate, enum compliance rate, null-vs-hallucinated rate on optional fields

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/structured-outputs/requirements.txt`

## Run

```bash
cd labs/structured-outputs
python lab-schema-design/main.py
```

## Expected output

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

## What to observe

- **Unconstrained:** parse success is 10/10, but `enum_violations > 0` and `hallucinated_optionals > 0` — especially on adversarial inputs with no contact info (inputs 4–5); the model guesses values for absent fields
- **Constrained:** `enum_violations` drops to 0; optional fields return `None` instead of fabricated values — the schema shape enforces `None` even when the model would otherwise fill in a guess

## Concepts verified

- [ ] `Literal` maps enum to JSON Schema `enum` — eliminates out-of-vocabulary values
- [ ] `str | None = None` returns `None` instead of a hallucinated value when field is absent
- [ ] `Field(max_length=...)` bounds string length
- [ ] Schema constraints do not degrade parse success rate — constrained and unconstrained succeed equally on parseable inputs

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `ContactConstrained`, change `role: Literal["engineer", "manager", "executive", "unknown"] = "unknown"` to `role: str | None = None`
- **Expected degradation:**
  - `enum_violations` stays 0 — there is no enum to violate
  - Non-standard values such as `"director"`, `"developer"`, or `"CEO"` pass through unchecked
  - The constrained schema no longer enforces vocabulary bounds on `role`
  - The `enum_violations` metric becomes meaningless as a comparison signal

Restore the `Literal` type on `role` after the experiment.
