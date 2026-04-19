---
id: "structured-outputs-readme"
title: "Structured Outputs"
type: "step-readme"
step: "structured-outputs"
path: "docs/structured-outputs/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "structured-output"
  - "tool-use"
  - "function-calling"
  - "json-schema"
  - "tool-patterns"

prerequisites:
  - "docs/prompt-engineering/README.md"
  - "docs/llm-apis/openai-api.md"

next:
  - "docs/structured-outputs/structured-outputs.md"

related:
  - "docs/rag/README.md"
  - "docs/ai-agents/README.md"

implementation_refs:
  - "labs/structured-outputs/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Covers how to extract structured data from LLM responses using schema enforcement and function calling — moving from format-spec prompts to guaranteed JSON, typed tool invocations, and composable tool patterns."
---

# Structured Outputs

## Navigation

[Docs](../README.md) / Structured Outputs

---

## 1. Overview

Prompting the model to respond in JSON works most of the time — but not reliably enough for production. A model can deviate from the requested schema on complex inputs, add explanatory prose outside the JSON block, or omit required fields under load. Structured outputs solve this at the API level: the provider validates the response against a declared schema before returning it, making format compliance a guarantee rather than a best-effort instruction.

Tool use (function calling) extends this further: instead of producing data, the model decides which function to call and with what arguments — structured as a typed object. The application executes the function, returns the result, and the model incorporates it into its response. This is the foundation of agentic behavior.

This step covers both mechanisms and the patterns that arise when combining them.

---

## 2. Scope

**Covered:**
- Structured output enforcement: JSON mode and response format schemas
- Tool use: declaring tools, model-generated tool calls, executing tools, returning results
- Tool patterns: single tool, parallel calls, sequential chains, router pattern
- Schema design: Pydantic models, JSON Schema constraints, field selection for reliability

**Not covered:**
- Multi-agent systems where tools call other agents (see `ai-agents`)
- RAG retrieval as a tool (see `rag`)
- Evaluation of structured output quality (see `evaluation-testing`)
- Prompt design for tool use (see `prompt-engineering`)

---

## 3. Key Concepts

**Structured output**
A model response that conforms to a declared JSON Schema, enforced at the API level so that invalid responses are rejected or corrected before being returned to the caller.

**Tool use**
A mechanism by which the model, instead of generating a text response, generates a structured function call — specifying which tool to invoke and what arguments to pass. The application executes the tool and returns the result.

**Function calling**
The OpenAI/Anthropic term for tool use: the model emits a `tool_calls` (OpenAI) or `tool_use` (Anthropic) content block specifying the function name and JSON-serialized arguments.

**JSON Schema**
A vocabulary for describing the structure, types, and constraints of JSON data. Used both for structured output enforcement and for declaring tool parameter shapes.

**Tool patterns**
Recurring compositions of tool calls: single tool (one invocation per turn), parallel tools (multiple independent tools in one turn), sequential chain (output of one tool feeds the next), and router (model selects which tool applies).

---

## 4. Concept Map

```
structured-output
    │
    ├── json-mode ──► API-enforced JSON without schema
    └── response-format ──► API-enforced JSON against declared schema
                                    │
                                    ▼
                             json-schema ◄── pydantic-model
                                    │
                                    ▼
tool-use ──────────────────► function-calling
    │                               │
    ├── tool-declaration             ├── tool_calls (OpenAI)
    ├── tool-call (model output)     └── tool_use block (Anthropic)
    └── tool-result (app returns)
                │
                ▼
        tool-patterns
            ├── single-tool
            ├── parallel-tools
            ├── sequential-chain
            └── router-pattern
```

---

## 5. Learning Flow

| Order | Topic | Dependency |
|-------|-------|------------|
| 1 | `structured-outputs.md` | prompt-engineering |
| 2 | `tool-usage.md` | structured-outputs.md |
| 3 | `tool-patterns.md` | tool-usage.md |
| 4 | `schema-design.md` | structured-outputs.md, tool-usage.md |
| 5 | `architecture.md` | all topics |
| 6 | `implementation-reference.md` | architecture |
| 7 | `validation.md` | all above |

---

## 6. Documentation Structure

```text
docs/structured-outputs/
├── README.md                    ← this file
├── structured-outputs.md        ← JSON mode and schema-enforced responses
├── tool-usage.md                ← declaring tools and the tool call cycle
├── tool-patterns.md             ← single, parallel, sequential, router patterns
├── schema-design.md             ← JSON Schema and Pydantic for reliability
├── architecture.md              ← system-level view
├── implementation-reference.md  ← bridge to lab execution
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-structured-outputs` | implementation | Extract typed data from text using schema-enforced JSON responses |
| `lab-tool-usage` | implementation | Implement the full tool call cycle: declare → invoke → execute → return |
| `lab-tool-patterns` | implementation | Build single, parallel, and sequential tool compositions |
| `lab-schema-design` | implementation | Design and test schemas for reliability across edge-case inputs |

`lab-schema-design` is optional. The first three are required.

---

## 8. How to Use This Step

**Recommended path:**
1. Read this README.
2. Read `structured-outputs.md` and run `lab-structured-outputs`.
3. Read `tool-usage.md` and run `lab-tool-usage`.
4. Read `tool-patterns.md` and run `lab-tool-patterns`.
5. Read `schema-design.md` — run `lab-schema-design` if available.
6. Read `architecture.md` and `implementation-reference.md`.
7. Complete `validation.md`.

---

## 9. Relationship to Other Steps

| Position | Step | Relationship |
|----------|------|--------------|
| Before | `prompt-engineering` | Output format specification via prompt is the precursor; this step replaces best-effort instruction with API enforcement |
| After | `rag` | Retrieval pipelines return structured results that feed into prompt context |
| Later dependency | `ai-agents` | Agent tool use loops are direct extensions of the tool call cycle established here |
| Later dependency | `evaluation-testing` | Evaluating structured output quality requires the schema definitions introduced here |

---

## 10. Next Steps

→ [`docs/structured-outputs/structured-outputs.md`](./structured-outputs.md)

---

## 11. Engineering Takeaways

### What This Adds

Schema-enforced responses and typed function calling — the transition from best-effort prompt formatting to API-level guarantees. This module introduces the tool call cycle that underlies all agentic behavior and provides the integration contract between LLM output and downstream system components.

### Engineering Trade-offs

| Decision | Benefit | Cost | When it breaks |
|----------|---------|------|----------------|
| JSON mode vs schema enforcement | Faster to set up; broader provider support | No schema guarantee; validation still required in client | Model produces valid JSON that violates schema; downstream parsing fails |
| Pydantic model vs raw JSON Schema | Type-safe, IDE-supported, auto-serialized | Python-only; schema changes require code changes | Schema drift between model definition and API call; serialization errors |
| Parallel tool calls vs sequential | Lower latency for independent operations | Harder to debug; results arrive out of expected order | Tool A's result is needed by tool B; parallel execution produces incorrect state |
| Router pattern vs explicit tool selection | Model selects the right tool; flexible | Model may route incorrectly; silent wrong-tool execution | Input is ambiguous; model picks a plausible but wrong tool without error |

### When NOT to Use This

- When the output is human-readable prose only — schema enforcement adds complexity without benefit.
- When tool use adds a round-trip per operation and latency is a hard constraint — benchmark first.
- When the schema is so large that it consumes significant context tokens — prune or split the schema.

### Common Failure Modes

- **Failure:** Tool hallucination — model calls a non-existent tool or invents arguments.
  **Cause:** Tool descriptions are ambiguous or overlap; model cannot distinguish between them.
  **Signal:** `tool_calls` content references a tool name not in the registered set.

- **Failure:** Schema too strict — model output consistently fails validation.
  **Cause:** Schema has too many required fields or overly narrow type constraints for the model to satisfy reliably.
  **Signal:** High validation failure rate; model often returns partial or coerced JSON.

- **Failure:** Tool result not returned — model generates a second tool call instead of a final answer.
  **Cause:** Tool result message appended with wrong role or format; model re-enters tool selection loop.
  **Signal:** Repeated tool calls for the same operation; loop does not terminate on `stop`.

### What Changes vs Traditional Systems

The model becomes a decision-making component in the control flow, not just a text generator. Tool calls express intent, not execution — the application retains responsibility for running tools and returning results. This inverts the traditional request/response model: the LLM drives the sequence, not the caller.

### Operational Considerations

- Required: schema registry or Pydantic model versioning strategy; tool execution sandbox with error handling.
- Observable: tool call frequency per turn, tool selection distribution, schema validation failure rate.
- Cost drivers: parallel tool calls increase per-call output token count; sequential chains multiply round-trips.
- Debugging: log the full `tool_calls` block and each `tool_result` message for every request.
- Scaling: tool execution latency is additive per sequential step; design for parallel execution where possible.

### Minimal Adoption Heuristic

**Use this when:**
- Downstream systems require machine-readable, typed output from the model.
- You are building any form of tool use, function dispatch, or agentic loop.

**Avoid this when:**
- The response is consumed only by a human — schema enforcement adds latency and complexity without value.
- A simpler prompt-level format instruction produces reliable enough output for the use case.
