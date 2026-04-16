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
