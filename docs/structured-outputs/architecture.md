---
id: "structured-outputs-architecture"
title: "Structured Outputs — Architecture"
type: "architecture"
step: "structured-outputs"
path: "docs/structured-outputs/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "structured-output"
  - "tool-use"
  - "tool-patterns"
  - "json-schema"

prerequisites:
  - "docs/structured-outputs/README.md"

next:
  - "docs/structured-outputs/implementation-reference.md"

related:
  - "docs/structured-outputs/structured-outputs.md"
  - "docs/structured-outputs/tool-usage.md"
  - "docs/structured-outputs/tool-patterns.md"
  - "docs/structured-outputs/schema-design.md"

implementation_refs:
  - "labs/structured-outputs/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the system-level architecture of structured output enforcement and tool use, covering the five components, data flows, and the tool call loop."
---

## 1. System Overview

The structured outputs system sits at the boundary between LLM response generation and application logic. Its purpose is to ensure that model output can be consumed programmatically — either as a typed data object (structured output path) or as a dispatched function call (tool use path). Both paths share a common schema declaration layer and converge at a normalized result consumed by application code.

The system has five components: Schema Registry, Request Builder, LLM Provider, Response Validator, and Tool Executor. The Response Validator and Tool Executor are active only on their respective paths.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| Schema Registry | Constraint declaration | Holds Pydantic models and JSON Schema definitions; generates API-compatible schema objects |
| Request Builder | API request assembly | Attaches `response_format` or `tools` to the outbound request; normalizes provider-specific field names |
| LLM Provider | Generation + enforcement | Generates the response; enforces schema conformance before returning (structured output) or emits a tool call object (tool use) |
| Response Validator | Output parsing | Deserializes the response into a typed Pydantic instance; raises on schema mismatch |
| Tool Executor | Function dispatch | Maps tool call name to registered function; executes with deserialized arguments; returns result string |

---

## 3. Component Interactions

The Schema Registry is the single source of truth. Both the Request Builder (which extracts the API schema) and the Response Validator (which uses the Pydantic model to validate) consume it. The Tool Executor is registered against the same schema — tool declarations use the same JSON Schema vocabulary as response format declarations.

The Request Builder owns provider normalization: it translates the application's tool list and response format declaration into the provider-specific API request shape (OpenAI `response_format` vs Anthropic `tools`).

The LLM Provider is a black box from the application's perspective. Its output is either a structured text response (enforced by schema) or a tool call object (driven by the declared tool list).

---

## 4. Data Flow

### Structured output path

```text
Input text
    │
    ▼
Request Builder ──── Schema Registry ────► JSON Schema
    │                                       (response_format)
    ▼
LLM Provider (enforces schema internally)
    │
    ▼
Raw JSON response string
    │
    ▼
Response Validator ──── Schema Registry ────► Pydantic model
    │                                          (validation)
    ▼
Typed Python object (e.g. ReviewSummary)
    │
    ▼
Application logic
```

### Tool use path

```text
User query
    │
    ▼
Request Builder ──── Schema Registry ────► Tool declarations
    │                                       (tools list + parameter schemas)
    ▼
LLM Provider
    │  finish_reason == "tool_calls"
    ▼
Tool call object (name + arguments JSON)
    │
    ▼
Tool Executor ──► dispatch(name, args) ──► registered function
    │
    ▼
Result string
    │
    ▼
Request Builder (append tool result to history)
    │
    ▼
LLM Provider (final call)
    │
    ▼
Final text response
    │
    ▼
Application logic
```

---

## 5. Execution Flow

### Structured output (single call)

1. Application declares a Pydantic model in the Schema Registry.
2. Request Builder generates the JSON Schema and attaches it as `response_format`.
3. LLM Provider generates and validates the response internally.
4. Response Validator deserializes the response into the Pydantic model.
5. Application consumes the typed object.

### Tool use loop (single tool)

1. Application registers tools (name, description, parameter schema).
2. Request Builder attaches the tool list to the request.
3. LLM Provider returns with `finish_reason == "tool_calls"`.
4. Application reads `tool_calls`, extracts function name and arguments.
5. Tool Executor dispatches to the registered function.
6. Result is appended to message history as a `tool` role message.
7. Request Builder sends the updated history.
8. LLM Provider returns with `finish_reason == "stop"`.
9. Application reads the final text response.

### Tool use loop (parallel tools)

Steps 3–6 above iterate over a list of tool calls rather than a single call. All results are appended before the next model invocation. The loop may repeat if the model emits another set of parallel calls.

---

## 6. Integration Points

**Upstream — prompt-engineering:** System prompt and instruction design determines what information the model uses to populate schema fields. Output format specification (prompt-side) is the precursor to schema enforcement (API-side).

**Upstream — llm-apis:** The Request Builder extends the base chat completion API with schema fields. The provider abstraction from `llm-apis` (`ChatResponse` normalization) is extended here to normalize tool call objects across providers.

**Downstream — rag:** Retrieval results are often returned as tool call results. The schema design for retrieval tools follows the same principles as any other tool parameter schema.

**Downstream — ai-agents:** Agent loops are extensions of the tool use execution flow. An agent adds persistence (tool results feed back into next-turn context), planning (the model determines which tool to call next), and termination conditions.

---

## 7. Trade-offs and Design Decisions

**Pydantic as the single schema source.** The alternative is maintaining separate JSON Schema files for the API call and dataclass definitions for application code. Pydantic eliminates this duplication at the cost of a Pydantic dependency in every layer that touches schema definitions. Given that Pydantic is already widely used in Python applications, this is an acceptable dependency.

**Tool Executor as a registry (not inline dispatch).** Dispatching by tool name via a registry (`{"get_weather": get_weather_fn}`) instead of inline `if/elif` blocks keeps the dispatch logic isolated, testable, and extensible without modifying the loop code. The cost is explicit registration boilerplate.

**Provider normalization in the Request Builder.** Normalizing provider differences at the request boundary keeps the Tool Executor and Response Validator provider-agnostic. The alternative — provider-specific branches throughout the application — is harder to maintain and test.

**Schema enforcement vs prompt-only.** Schema enforcement adds one round-trip of internal provider latency (the provider validates and potentially retries). For applications where format reliability outweighs latency, enforcement is the right choice. For low-stakes internal tools, prompt-only may be sufficient.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| Schema Registry + Response Validator | `lab-structured-outputs` |
| Tool Executor + Request Builder (tool use path) | `lab-tool-usage` |
| Tool Executor (parallel, sequential, router) | `lab-tool-patterns` |
| Schema Registry (constraint design + reliability testing) | `lab-schema-design` |

---

## 9. Limitations and Boundaries

**Schema enforcement is provider-dependent.** OpenAI strict mode, Ollama model-level support, and Anthropic tool-based enforcement have different reliability characteristics. The architecture assumes a single provider per deployment; multi-provider failover requires additional normalization.

**Tool Executor has no sandboxing.** Tools execute with full application privileges. The architecture does not impose isolation, rate limiting, or capability checks on tool execution. These are application-level responsibilities outside this scope.

**Response Validator parses, not evaluates.** Validation confirms the response matches the schema shape. Semantic correctness — whether the extracted values are accurate — is not the validator's concern. Evaluation belongs to the `evaluation-testing` module.

**Context growth in tool loops.** Each tool call round-trip adds messages to the history. The architecture does not define a truncation strategy. Long-running tool loops require context management, which is covered in the `memory-context` module.

---

## 10. Summary

The structured outputs architecture has two paths sharing a common schema layer: the structured output path enforces response format at the API level and deserializes into typed objects; the tool use path lets the model drive function dispatch while the application retains execution control. The Schema Registry (Pydantic) and Request Builder (provider normalization) are the key structural components. The tool use loop — generate → call → execute → return → generate — is the primitive from which parallel, sequential, and router patterns are composed, and from which agent loops are built.
