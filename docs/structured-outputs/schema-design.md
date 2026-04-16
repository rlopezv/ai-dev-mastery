---
id: "structured-outputs-schema-design"
title: "Schema Design"
type: "topic"
step: "structured-outputs"
path: "docs/structured-outputs/schema-design.md"
status: "draft"
level: "intermediate"

concepts:
  - "json-schema"
  - "pydantic-model"
  - "schema-constraints"
  - "field-selection"

prerequisites:
  - "docs/structured-outputs/structured-outputs.md"
  - "docs/structured-outputs/tool-usage.md"

next:
  - "docs/structured-outputs/architecture.md"

related:
  - "docs/structured-outputs/tool-patterns.md"

implementation_refs:
  - "labs/structured-outputs/lab-schema-design"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers how to design JSON Schema and Pydantic models that maximize structured output reliability — field selection, constraint types, enum usage, and nesting trade-offs."
---

## 1. Intuition

Schema enforcement guarantees the output conforms to a shape, but the shape itself must be designed for the model to fill correctly. A schema that demands fields the input cannot provide, uses unconstrained string types where enums would work, or nests objects four levels deep will produce valid JSON with wrong values. Schema design is the practice of matching the declared contract to what the model can reliably produce from the available input.

---

## 2. Explanation

### 2.1 Why

Format compliance and semantic quality are separate concerns. Schema enforcement handles the first; schema design addresses the second. A poorly designed schema shifts the failure mode from "invalid JSON" to "valid JSON with hallucinated or default values" — a worse failure because it passes format validation silently.

The design goal is: every declared field should be fillable from the input, every constraint should narrow the output to the useful range, and every optional field should be genuinely optional rather than a fallback for uncertainty.

### 2.2 How

**Field selection.** Declare only the fields the application will use. Each additional field is a new surface for the model to guess. If the application only uses `sentiment` and `score`, do not declare `author`, `language`, or `confidence` — even if they might be useful later.

**Type constraints.** Use the most restrictive type that fits the data:
- `enum` instead of unconstrained `string` for categorical values (`"positive" | "neutral" | "negative"` rather than `string`).
- `integer` with `minimum`/`maximum` for bounded counts.
- `number` for continuous values.
- `boolean` for binary flags rather than `"yes"` / `"no"` strings.

**Required vs optional.** Mark a field `required` only if the input reliably contains the information needed to fill it. An optional field should have a `default` value that represents "not present" rather than a hallucinated value. A field that is sometimes absent should be declared optional and handled as `None` in application code.

**Nesting.** Flat schemas are more reliable than deeply nested ones. A two-level schema (object with scalar fields) has lower failure rate than a three-level schema. If nesting is necessary, keep it to one additional level and use `additionalProperties: false` at each level.

**Array fields.** Arrays of strings are reliable. Arrays of nested objects increase failure rate with each additional required field per item. If the application needs a list of structured items, consider whether a flat array of strings with a post-processing step is sufficient.

**Pydantic model design:**

```python
# See: labs/structured-outputs/lab-schema-design/main.py
from pydantic import BaseModel, Field
from typing import Literal

class IssueReport(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    title: str = Field(max_length=80, description="One-line issue description")
    affected_component: str
    reproducible: bool
    steps_to_reproduce: list[str] = Field(
        default_factory=list,
        description="Empty list if not reproducible or unknown"
    )
```

`Literal` maps to `enum` in JSON Schema. `Field(max_length=...)` adds a `maxLength` constraint. `default_factory=list` marks the field optional with an empty-list default.

**JSON Schema equivalents:**

```json
{
  "type": "object",
  "properties": {
    "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
    "title": {"type": "string", "maxLength": 80},
    "affected_component": {"type": "string"},
    "reproducible": {"type": "boolean"},
    "steps_to_reproduce": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["severity", "title", "affected_component", "reproducible"],
  "additionalProperties": false
}
```

### 2.3 Code example

```python
# See: labs/structured-outputs/lab-schema-design/main.py
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI

class ContactExtraction(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    role: Literal["engineer", "manager", "executive", "unknown"] = "unknown"

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def extract_contact(text: str) -> ContactExtraction:
    response = client.beta.chat.completions.parse(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "Extract contact information from the text."},
            {"role": "user", "content": text},
        ],
        response_format=ContactExtraction,
    )
    return response.choices[0].message.parsed

# Edge case: no phone or company in input → optional fields return None, not hallucinated values
result = extract_contact("Email John Smith at john@acme.com about the project.")
print(result.name, result.email, result.phone)  # "John Smith", "john@acme.com", None
```

---

## 3. Table

| Schema element | Better choice | Reason |
|----------------|---------------|--------|
| Categorical string | `enum` / `Literal` | Eliminates free-form hallucination |
| Bounded integer | `integer` + `minimum`/`maximum` | Prevents out-of-range values |
| Binary flag | `boolean` | Removes ambiguous string variants |
| Unknown-able string | `string \| null` with `default: null` | Returns None instead of guessing |
| Nested object | Flat fields where possible | Reduces constraint complexity |
| Deep array of objects | Array of strings + post-processing | Lower per-item failure rate |

| Pydantic annotation | JSON Schema output | Effect |
|--------------------|--------------------|--------|
| `Literal["a", "b"]` | `{"enum": ["a", "b"]}` | Constrained to listed values |
| `Field(max_length=80)` | `{"maxLength": 80}` | Length-bounded string |
| `str \| None = None` | Optional field, nullable | Safe absent-field handling |
| `list[str]` | `{"type": "array", "items": {"type": "string"}}` | Flat string array |
| `additionalProperties: false` | Blocks unlisted fields | Strict output shape |

---

## 4. Engineering Implications

**Schema is a reliability investment.** Moving from unconstrained strings to enums typically increases extraction accuracy by 10–30% on ambiguous inputs. The investment is a few lines of Pydantic; the return is fewer downstream validation errors.

**Optional fields change the error surface.** A `required` field on absent information forces the model to guess. An `optional` field on absent information returns `None`. Application code that handles `None` explicitly is more robust than code that validates guessed values.

**`additionalProperties: false` in strict mode.** OpenAI strict mode enforces this automatically. In non-strict mode, explicitly setting it prevents the model from adding helpful but undeclared fields that break deserialization.

**Schema evolution.** Adding a new optional field with a default is backward-compatible. Adding a new required field breaks existing inputs that cannot provide it. Version schemas the same way you version APIs: optional additions are non-breaking; required additions are breaking changes.

**Tool schema vs response format schema.** Both use JSON Schema, but serve different goals. Response format schema shapes what the model produces; tool parameter schema shapes what the model sends to your function. The design principles are the same: minimal, constrained, matching what the model can reliably infer.

---

## 5. Implementation Connection

`lab-schema-design` (optional) tests schema choices against adversarial inputs:

1. A baseline schema with unconstrained string types for all fields.
2. A constrained schema with enums, bounded integers, and optional nullable fields.
3. A test harness running both schemas over 10+ inputs, including edge cases with missing data, ambiguous values, and unusual formats.

The lab measures: parse success rate, enum compliance rate, and rate of `None` vs hallucinated values on absent fields. The constrained schema consistently outperforms the unconstrained baseline.

---

## 6. Failure Modes and Limitations

**Enum over-restriction.** If the real-world data has more categories than the declared enum, the model will map out-of-vocabulary values to the closest enum member. This is silent and incorrect. Enums work best when the category space is genuinely closed.

**Schema drift.** The Pydantic model in application code and the JSON Schema sent to the API must stay synchronized. If you manually edit one and forget the other, the API call and the deserialization diverge. Use Pydantic's `model_json_schema()` to generate the API schema from the model, not the other way around.

**Pydantic validation vs API enforcement.** Schema enforcement at the API level guarantees the response matches the schema. Pydantic's `model_validate` adds a second validation pass in application code. Both should be in place: API enforcement handles format; Pydantic validation handles application-level invariants like cross-field dependencies.

**Unsupported constraints.** Not all JSON Schema keywords are supported in strict mode. Recursive schemas (`$ref` to self), `oneOf`/`anyOf` for union types, and `patternProperties` may be rejected or ignored. Test the specific provider against your schema before deploying.

---

## 7. Summary

Schema design is the layer between format compliance and semantic reliability. Field selection, enum constraints, bounded types, and explicit nullable fields each reduce the surface area for model errors. Pydantic models are the practical tool: they generate the API schema and validate the deserialized output from a single declaration. A well-designed schema turns structured output from a format guarantee into a semantic reliability investment.
