---
id: "structured-outputs-tool-usage"
title: "Tool Usage"
type: "topic"
step: "structured-outputs"
path: "docs/structured-outputs/tool-usage.md"
status: "draft"
level: "intermediate"

concepts:
  - "tool-use"
  - "function-calling"
  - "tool-declaration"
  - "tool-call"
  - "tool-result"

prerequisites:
  - "docs/structured-outputs/structured-outputs.md"

next:
  - "docs/structured-outputs/tool-patterns.md"

related:
  - "docs/structured-outputs/schema-design.md"
  - "docs/ai-agents/README.md"

implementation_refs:
  - "labs/structured-outputs/lab-tool-usage"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains the tool use mechanism — declaring tools, the model-generated tool call, application execution, and result return — as the foundation of model-driven function invocation."
---

## 1. Intuition

A standard LLM call is a one-shot exchange: you send a message, the model generates text. Tool use changes the shape of the exchange: instead of generating text, the model can generate a function call — a structured object specifying which function to invoke and with what arguments. The application executes that function and sends the result back to the model, which then produces the final response. The model does not execute code; it decides what to call. The application executes and returns.

---

## 2. Explanation

### 2.1 Why

Text generation cannot reliably produce real-time data, perform arithmetic, query a database, or take an action in an external system. Tool use gives the model a mechanism to delegate those operations. The model contributes reasoning about which operation is needed and what arguments to supply; the application contributes the actual execution capability. This division keeps the model's job tractable and gives the application full control over what can be executed.

### 2.2 How

The tool use cycle has four phases:

**Phase 1 — Declaration.** The caller defines the available tools as a list of JSON Schema objects. Each tool has a `name`, a `description` (which the model reads to decide relevance), and a `parameters` schema (which constrains what the model can put in the arguments).

**Phase 2 — Model call.** The model receives the messages and the tool list. If it determines that a tool call is the appropriate response, it emits a tool call object instead of a text response. The call contains the tool name and a JSON-encoded arguments object that conforms to the declared parameter schema.

**Phase 3 — Application execution.** The application inspects the tool call, looks up the corresponding function, validates the arguments (optional but recommended), and executes it. This step happens entirely in application code — the model is not involved.

**Phase 4 — Result return.** The application appends the tool call to the message history (as an `assistant` message), then appends a `tool` role message containing the result. The model is called again with the extended history and produces the final response incorporating the tool's output.

**OpenAI schema:**
- Tool call in response: `response.choices[0].message.tool_calls[0]` — contains `id`, `function.name`, `function.arguments` (JSON string)
- Result message: `{"role": "tool", "tool_call_id": "<id>", "content": "<result>"}`

**Anthropic schema:**
- Tool call in response: content block with `"type": "tool_use"` — contains `id`, `name`, `input` (already a dict)
- Result message: `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "<id>", "content": "<result>"}]}`

### 2.3 Code example

```python
# See: labs/structured-outputs/lab-tool-usage/main.py
import json
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Return current temperature for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["city"],
            },
        },
    }
]

# Phase 1 + 2: send with tools, model generates a tool call
messages = [{"role": "user", "content": "What is the temperature in Madrid?"}]
response = client.chat.completions.create(
    model="llama3.2", messages=messages, tools=tools, tool_choice="auto"
)

tool_call = response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

# Phase 3: application executes the function
def get_weather(city: str, unit: str = "celsius") -> str:
    return f"22 {unit}"  # stub

result = get_weather(**args)

# Phase 4: append tool call + result, get final response
messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result,
})

final = client.chat.completions.create(model="llama3.2", messages=messages)
print(final.choices[0].message.content)
```

---

## 3. Table

| Phase | Actor | Input | Output |
|-------|-------|-------|--------|
| Declaration | Application | Tool definitions (name, description, parameters) | Tool list sent to API |
| Model call | Model | Messages + tool list | Tool call object (name + arguments) |
| Execution | Application | Tool call arguments | Result (string or JSON) |
| Result return | Application + Model | Extended message history | Final text response |

| Field | OpenAI | Anthropic |
|-------|--------|-----------|
| Tool call type | `response.choices[0].message.tool_calls` | Content block `type: "tool_use"` |
| Arguments format | JSON string (`function.arguments`) | Dict (`input`) |
| Result role | `"tool"` | `"user"` (with `tool_result` content block) |
| Result ID field | `tool_call_id` | `tool_use_id` |
| Finish reason when calling | `"tool_calls"` | `"tool_use"` |

---

## 4. Engineering Implications

**The model cannot be trusted to call only declared tools.** Some models attempt to call tools not in the list, or generate arguments that fail validation. Always validate `tool_call.function.name` against the registered tool set before executing.

**`tool_choice` controls invocation behavior.** Setting `tool_choice="auto"` lets the model decide whether to call a tool. `tool_choice="required"` forces a call. `tool_choice={"type": "function", "function": {"name": "..."}}` forces a specific call. Use `"required"` when you need structured output from every call — this effectively makes tool use an alternative structured output path.

**Arguments are a JSON string in OpenAI, a dict in Anthropic.** Normalizing this difference in a shared abstraction prevents provider-specific branching throughout the application.

**Multi-tool responses.** The model can emit multiple tool calls in a single response (parallel tool use). The application must handle a list of calls and return a result message for each before the model can continue.

**Finish reason detection is mandatory.** Before reading `tool_calls`, check that `finish_reason == "tool_calls"` (OpenAI) or the stop reason is `"tool_use"` (Anthropic). A response that stopped for other reasons will not have a tool call.

---

## 5. Implementation Connection

`lab-tool-usage` implements the complete tool call cycle:

1. A single tool (`get_current_time` or `lookup_exchange_rate`) is declared.
2. The model generates the tool call.
3. The application executes the function and captures the result.
4. The result is returned and the final response is extracted.

Observe the `finish_reason` field in the first response (`"tool_calls"`) versus the second (`"stop"`). Observe the structure of `tool_calls[0]` — particularly that `arguments` is a JSON string requiring `json.loads`. The lab also demonstrates the Anthropic path to surface the schema difference.

---

## 6. Failure Modes and Limitations

**Missing finish reason check.** If the model does not call a tool (returns `"stop"` instead of `"tool_calls"`), accessing `message.tool_calls` returns `None`. Unguarded index access raises a `TypeError`. Always check `finish_reason` before branching.

**Argument hallucination.** The model may generate arguments that satisfy the JSON Schema syntactically but are semantically incorrect — a city name that doesn't exist, a date in the wrong format. Schema enforcement prevents type errors; semantic validation is the application's responsibility.

**No execution isolation.** The application decides what tools are available and executes them with full application privileges. A tool that writes to a database or calls an external API will do so whenever the model calls it. Tool declarations are a capability grant — scope them carefully.

**Infinite loops in agentic use.** If the tool result causes the model to emit another tool call indefinitely (for example, a tool that returns data the model always wants to refine), the loop runs until a token budget or iteration limit is hit. Tool use loops require explicit termination conditions.

---

## 7. Summary

Tool use gives the model a structured mechanism to delegate function execution to the application. The model declares intent (which function, what arguments); the application executes and returns the result. The cycle is driven by the `finish_reason`: detect `"tool_calls"`, execute, return results, and call again until `"stop"`. This four-phase loop is the primitive from which all agentic behavior is built.
