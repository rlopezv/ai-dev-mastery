---
id: "structured-outputs-implementation-reference"
title: "Structured Outputs — Implementation Reference"
type: "implementation-reference"
step: "structured-outputs"
path: "docs/structured-outputs/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "structured-output"
  - "tool-use"
  - "pydantic-model"
  - "tool-patterns"

prerequisites:
  - "docs/structured-outputs/architecture.md"

next:
  - "docs/structured-outputs/validation.md"

related:
  - "docs/structured-outputs/structured-outputs.md"
  - "docs/structured-outputs/tool-usage.md"
  - "docs/structured-outputs/tool-patterns.md"
  - "docs/structured-outputs/schema-design.md"

implementation_refs:
  - "labs/structured-outputs/lab-structured-outputs"
  - "labs/structured-outputs/lab-tool-usage"
  - "labs/structured-outputs/lab-tool-patterns"
  - "labs/structured-outputs/lab-schema-design"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Maps the structured outputs architecture to implementation patterns — schema declaration with Pydantic, tool registry, tool call loop, and parallel result accumulation."
---

## 1. Implementation Overview

The architecture defines five components: Schema Registry, Request Builder, LLM Provider, Response Validator, and Tool Executor. In implementation:

- The **Schema Registry** is a Pydantic model class. It generates JSON Schema on demand via `model_json_schema()` and validates deserialized output via `model_validate()`.
- The **Request Builder** is the call site: `client.beta.chat.completions.parse(response_format=MyModel)` for structured output; `client.chat.completions.create(tools=[...])` for tool use.
- The **Response Validator** is `response.choices[0].message.parsed` for structured output (SDK handles deserialization) or `json.loads(tool_call.function.arguments)` for tool arguments.
- The **Tool Executor** is a dict mapping tool names to callable functions, with a dispatch function wrapping it.

The labs implement each component in isolation before composing them.

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| Pydantic response format | Declare schema as Pydantic model; pass to `response_format`; read `message.parsed` | Any structured data extraction from unstructured text |
| Tool registry dispatch | Dict of `{name: callable}`; look up by `tool_call.function.name` before executing | Tool use loops; prevents `if/elif` chains |
| Finish-reason gate | Check `finish_reason` before branching to tool call or final response handling | Every tool use loop iteration |
| Parallel result accumulation | Iterate `message.tool_calls`; append one `tool` message per call | Responses with multiple simultaneous tool calls |
| Sequential chain | Hard-code pipeline steps; each step's output is the next step's input | Invariant pipelines with data dependencies between steps |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| Schema Registry | `class MyModel(BaseModel)` — Pydantic model with field annotations and `Field(...)` constraints |
| Request Builder (structured output) | `client.beta.chat.completions.parse(response_format=MyModel)` |
| Request Builder (tool use) | `client.chat.completions.create(tools=TOOL_DEFINITIONS, tool_choice="auto")` |
| Response Validator | `response.choices[0].message.parsed` (SDK) or `MyModel.model_validate(data)` |
| Tool Executor | `TOOL_REGISTRY = {"name": fn}` + `dispatch(name, args_json)` |
| Tool result message | `{"role": "tool", "tool_call_id": id, "content": result}` |

---

## 4. Data Structures and Interfaces

```python
# Orientative — see labs/structured-outputs/lab-structured-outputs/main.py for full implementation

from pydantic import BaseModel, Field
from typing import Literal

# Schema Registry: Pydantic model as single source of schema truth
class ExtractionResult(BaseModel):
    category: Literal["bug", "feature", "question", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(max_length=120)
    requires_follow_up: bool
    affected_components: list[str] = Field(default_factory=list)
```

```python
# Orientative — see labs/structured-outputs/lab-tool-usage/main.py for full implementation
import json
from typing import Callable

# Tool Executor: name → callable registry
TOOL_REGISTRY: dict[str, Callable] = {}

def register_tool(name: str):
    """Decorator to register a function as a tool."""
    def wrapper(fn: Callable) -> Callable:
        TOOL_REGISTRY[name] = fn
        return fn
    return wrapper

def dispatch(tool_name: str, arguments_json: str) -> str:
    """Execute a registered tool and return the result as a string."""
    if tool_name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{tool_name}'"
    args = json.loads(arguments_json)
    result = TOOL_REGISTRY[tool_name](**args)
    return str(result)
```

```python
# Orientative — see labs/structured-outputs/lab-tool-patterns/main.py for full implementation

# Tool call loop: finish-reason gate + parallel result accumulation
def tool_loop(client, messages: list[dict], tools: list[dict]) -> str:
    while True:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL, messages=messages, tools=tools
        )
        msg = response.choices[0].message
        finish = response.choices[0].finish_reason

        if finish == "stop":
            return msg.content

        if finish == "tool_calls":
            messages.append(msg)
            for call in msg.tool_calls:                     # parallel: iterate list
                result = dispatch(
                    call.function.name,
                    call.function.arguments,
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })
            # continue loop — model may call more tools or produce final response
```

```python
# Orientative — see labs/structured-outputs/lab-tool-patterns/main.py for full implementation

# Sequential chain: hard-coded pipeline
def sequential_weather_pipeline(client, city_query: str) -> str:
    # Step 1: resolve city name to coordinates
    coords = call_single_tool(client, city_query, "geocode_city")
    lat, lon = coords["lat"], coords["lon"]
    # Step 2: fetch weather using coordinates
    weather = call_single_tool(
        client, f"lat={lat} lon={lon}", "get_weather_by_coords"
    )
    return weather
```

---

## 5. Design Decisions

**Pydantic as the schema source.** Maintaining a Pydantic model generates the JSON Schema for the API call and validates the response from a single class definition. The alternative — a separate JSON Schema file and a separate dataclass — creates two artifacts that must stay synchronized. The Pydantic approach eliminates that drift.

**Tool registry over inline dispatch.** An `if/elif` dispatch block is simple for one or two tools but grows linearly with the number of tools and requires modifying the loop logic to add a tool. A registry decouples tool definition from loop logic: register once, dispatch by name. The loop becomes a stable inner loop that does not change as tools are added or removed.

**Finish-reason gate as the loop condition.** The loop terminates on `"stop"` and continues on `"tool_calls"`. This handles both single-call and multi-call scenarios without branching for each case. It also correctly handles models that complete without calling any tools — a valid outcome when `tool_choice="auto"`.

**Append assistant message before tool results.** The full assistant message (containing `tool_calls`) must be in the message history before tool results are appended. Omitting it causes the provider to reject the request because tool result messages reference `tool_call_id` values that don't appear in the history.

**Parallel execution is opt-in.** The tool loop iterates calls sequentially by default. For calls to external services with high latency, replace the `for` loop body with `asyncio.gather` or a thread pool. The loop structure supports this without modification.

---

## 6. External Dependencies

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| Ollama | LLM runtime (llama3.2) | `light` |
| `openai` SDK | Chat completions + tool use API client | `light` |
| `pydantic` | Schema declaration + response validation | `light` |
| `anthropic` SDK | Anthropic Messages API (tool use schema diff) | `light` |

---

## 7. Mapping to Labs

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| Pydantic response format + structured output enforcement | `lab-structured-outputs` | Schema enforcement reduces parse errors vs prompt-only JSON |
| Tool registry + finish-reason gate + result return | `lab-tool-usage` | Complete tool call cycle across OpenAI and Anthropic schemas |
| Parallel result accumulation | `lab-tool-patterns` | Multiple tool calls handled in one loop iteration |
| Sequential chain (hard-coded pipeline) | `lab-tool-patterns` | Data dependency between steps preserved without model involvement |
| Router pattern (model-driven dispatch) | `lab-tool-patterns` | Model selects among N tools based on query |
| Constraint design + adversarial input testing | `lab-schema-design` | Enum + nullable fields outperform unconstrained strings on edge cases |

---

## 8. Trade-offs and Constraints

**Schema strictness vs flexibility.** Strict mode (`additionalProperties: false`, all fields required) maximizes format reliability but breaks on inputs that cannot provide all declared fields. Relaxed mode (optional fields with defaults) handles partial inputs but requires explicit `None` handling in application code. The appropriate choice depends on how well-structured the input is.

**Tool choice control vs model autonomy.** `tool_choice="auto"` allows the model to decide whether to call a tool; `tool_choice="required"` forces a call. For structured output via tool use, `"required"` is more predictable. For conversational agents, `"auto"` preserves the model's ability to answer directly without a tool call.

**Loop depth and context growth.** Each round-trip appends messages to the history. A three-step sequential chain adds six messages (three tool calls + three results). Applications with long pipelines need to measure context growth and prune or summarize as needed.

**Pydantic strict mode vs coerce.** `model_validate(data, strict=True)` rejects type coercions (a string `"5"` will not coerce to integer `5`). For model output where the JSON Schema enforces types at the API level, this is the correct default. Without API-level enforcement, coerce mode is more tolerant of format edge cases.

---

## 9. Failure Modes

**Accessing `message.tool_calls` without checking `finish_reason`.** If the model returns a text response instead of a tool call, `message.tool_calls` is `None`. Indexing it raises `TypeError`. Always gate on `finish_reason == "tool_calls"` before accessing the list.

**Missing assistant message before tool results.** Appending tool result messages without first appending the assistant message that generated the calls causes a provider rejection. The provider validates that every `tool_call_id` in result messages has a corresponding call in the history.

**Registering a function under the wrong name.** The tool registry key must match the `name` field in the tool declaration exactly (case-sensitive). A mismatch returns an "unknown tool" error at dispatch time, not at registration time.

**Schema with required field the input cannot provide.** If the input text does not contain the information needed to fill a required field, the model will either refuse to generate, return an empty string, or hallucinate a plausible value. Mark fields optional when their presence depends on input content.

**Iterating `tool_calls` as if it were always length 1.** Single-indexing `msg.tool_calls[0]` silently ignores any additional tool calls when the model emits parallel calls. Always iterate the full list.

---

## 10. Summary

The implementation reduces to three patterns: Pydantic model as schema source (structured output path), tool registry + finish-reason loop (tool use path), and parallel accumulation (multi-call turn handling). The Pydantic model generates the API schema and validates the response from one declaration. The finish-reason gate is the loop condition. The registry decouples tool definition from loop logic. These three patterns compose to cover all four tool use patterns — single, parallel, sequential, and router — without structural changes to the loop.
