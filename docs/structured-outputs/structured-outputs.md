---
id: "structured-outputs-structured-outputs"
title: "Structured Outputs"
type: "topic"
step: "structured-outputs"
path: "docs/structured-outputs/structured-outputs.md"
status: "draft"
level: "intermediate"

concepts:
  - "structured-output"
  - "json-mode"
  - "response-format"
  - "json-schema"

prerequisites:
  - "docs/prompt-engineering/README.md"
  - "docs/llm-apis/openai-api.md"

next:
  - "docs/structured-outputs/tool-usage.md"

related:
  - "docs/structured-outputs/schema-design.md"

implementation_refs:
  - "labs/structured-outputs/lab-structured-outputs"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how JSON mode and response-format schema enforcement guarantee structured model output at the API level, replacing best-effort format instructions with provider-enforced constraints."
---

# Structured Outputs

## Navigation

[Docs](../README.md) / [Structured Outputs](README.md) / Structured Outputs

---

## 1. Intuition

Asking a model to "respond in JSON" is an instruction, not a contract. On typical inputs it works. On edge cases — long outputs, unusual values, models under load — the response may include prose before the JSON block, omit fields, or produce invalid syntax. JSON mode and response-format schema enforcement move the contract from the prompt to the API: the provider validates and retries internally, and the caller receives a guaranteed-valid response or an explicit error.

---

## 2. Explanation

### 2.1 Why

A production pipeline that parses model output breaks when format compliance fails. The cost of that failure — a runtime exception, a dropped record, a user-facing error — outweighs the cost of over-engineering the prompt. Structured output enforcement solves the problem at the right layer: instead of prompting more carefully, you declare a schema and let the API enforce it.

Two mechanisms exist:

- **JSON mode** — instructs the API to return syntactically valid JSON without constraining its shape. The model chooses field names and nesting. Useful when the output structure is flexible and the caller handles deserialization.
- **Response format (schema enforcement)** — attaches a JSON Schema to the request. The provider validates the response against it and retries or corrects before returning. The caller receives an object that matches the declared schema.

Schema enforcement is strictly stronger: it guarantees both valid JSON and structural conformance.

### 2.2 How

**JSON mode (OpenAI / Ollama-compatible):**

The caller sets `response_format={"type": "json_object"}` on the request. The model is constrained to emit only valid JSON. No schema is attached; the structure is model-determined.

**Response format with schema (OpenAI):**

The caller sets `response_format={"type": "json_schema", "json_schema": {"name": "...", "schema": {...}, "strict": true}}`. The provider enforces the schema before returning. With `strict: true`, the model is constrained to the declared fields only — no extra keys, no omissions.

**Pydantic integration:**

Pydantic models can generate JSON Schema automatically. The OpenAI Python SDK accepts a `response_format` parameter that takes a Pydantic model class directly, extracting the schema internally.

**Anthropic:**

Anthropic does not expose a dedicated JSON mode. The equivalent is a tool declaration with a single tool whose input schema defines the expected structure. The model is instructed to call that tool; the arguments are the structured output.

### 2.3 Code example

```python
# See: labs/structured-outputs/lab-structured-outputs/main.py
from pydantic import BaseModel
from openai import OpenAI

class ReviewSummary(BaseModel):
    sentiment: str          # "positive" | "neutral" | "negative"
    score: int              # 1-5
    key_issues: list[str]

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.beta.chat.completions.parse(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "Extract a review summary."},
        {"role": "user", "content": "The product arrived late and was damaged."},
    ],
    response_format=ReviewSummary,
)

summary: ReviewSummary = response.choices[0].message.parsed
print(summary.sentiment, summary.score, summary.key_issues)
```

---

## 3. Table

| Mechanism | Provider | Schema required | Guarantees |
|-----------|----------|-----------------|------------|
| JSON mode | OpenAI, Ollama | No | Syntactically valid JSON |
| Response format (json_schema) | OpenAI | Yes | Valid JSON + schema conformance |
| Tool use as structured output | Anthropic | Yes (tool input schema) | Valid JSON + schema conformance |
| Prompt-only ("respond in JSON") | Any | No | Best-effort; no API guarantee |

| Feature | JSON mode | Schema enforcement |
|---------|-----------|--------------------|
| Output shape controlled | No | Yes |
| Required fields guaranteed | No | Yes |
| Extra fields excluded | No | Yes (strict mode) |
| Pydantic integration | Manual deserialization | Native parse |
| Provider retry on failure | No | Yes |

---

## 4. Engineering Implications

**Schema enforcement changes the failure mode.** With prompt-only JSON, failures are silent: the response parses but has the wrong shape. With schema enforcement, failures are explicit: the API returns an error or the parsed object is `None`. Explicit failures are easier to handle and debug.

**Schema size affects latency.** Large schemas with many optional fields and nested objects increase the constraint complexity the model must satisfy. Keep schemas minimal: declare only the fields the application actually needs.

**Strict mode limits flexibility.** `strict: true` disallows any field not declared in the schema, including fields the model might add as helpful context. If the use case benefits from optional enrichment, use non-strict mode and validate programmatically after deserialization.

**Pydantic as a single source of truth.** Defining the schema as a Pydantic model gives you one object that generates the JSON Schema for the API call and validates the deserialized response in application code. This eliminates the drift that occurs when the schema declaration and the dataclass definition are maintained separately.

---

## 5. Implementation Connection

`lab-structured-outputs` demonstrates:

1. A baseline with prompt-only JSON format specification and manual parsing — shows the failure class this approach introduces.
2. JSON mode enabled — syntactic validity guaranteed, structural parsing still manual.
3. Schema enforcement via Pydantic model — structured response guaranteed, `response.choices[0].message.parsed` returns a typed object.

Observe the difference in error rate between the three approaches by running each over a set of adversarial inputs: long text, special characters, ambiguous classifications.

---

## 6. Failure Modes and Limitations

**Model capability boundary.** Schema enforcement constrains the output format but cannot improve the semantic quality of the model's answers. A model may produce a perfectly valid JSON object with incorrect field values. Schema enforcement is a format guarantee, not a correctness guarantee.

**Refusal on impossible schemas.** If the schema declares a `required` field that the model cannot reasonably populate — for example, `phone_number` in a text that contains no phone number — the model may refuse to generate, return a null value, or hallucinate a plausible value. Design schemas to match what the input can actually provide.

**Provider-specific availability.** JSON schema enforcement with `strict: true` is an OpenAI feature. Ollama's support depends on the model and version. Anthropic requires routing through tool use. Application code that relies on this feature is not provider-portable without an abstraction layer.

**Nested schema depth.** Deeply nested schemas with recursive references are not supported in strict mode. Flatten schemas where possible.

---

## 7. Summary

Structured output enforcement moves format compliance from prompt instructions to the API contract. JSON mode guarantees syntactic validity; schema enforcement guarantees structural conformance. Pydantic models serve as the single declaration from which both the API schema and the application dataclass are derived. The result is a parse-safe boundary between model output and application logic.
