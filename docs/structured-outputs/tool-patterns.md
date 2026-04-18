---
id: "structured-outputs-tool-patterns"
title: "Tool Patterns"
type: "topic"
step: "structured-outputs"
path: "docs/structured-outputs/tool-patterns.md"
status: "draft"
level: "intermediate"

concepts:
  - "tool-patterns"
  - "parallel-tools"
  - "sequential-chain"
  - "router-pattern"
  - "single-tool"

prerequisites:
  - "docs/structured-outputs/tool-usage.md"

next:
  - "docs/structured-outputs/schema-design.md"

related:
  - "docs/ai-agents/README.md"

implementation_refs:
  - "labs/structured-outputs/lab-tool-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes four recurring compositions of tool calls — single tool, parallel tools, sequential chain, and router — and the application logic required to implement each."
---

# Tool Patterns

## Navigation

[Docs](../README.md) / [Structured Outputs](README.md) / Tool Patterns

---

## 1. Intuition

A single tool call answers one question. Real applications need more: the model may need two independent data sources at once, or the output of one call may determine the next. These compositions follow four patterns. Knowing the pattern before building the application logic determines how many API round-trips are needed and how the result messages are structured.

---

## 2. Explanation

### 2.1 Why

Ad-hoc tool invocation code — one tool, one call — does not generalize to multi-tool scenarios. Each pattern requires a different message accumulation strategy and a different termination condition. Recognizing the pattern first avoids the trap of writing single-tool logic that breaks when the model emits two tool calls in one turn, or a sequential logic that calls the API unnecessarily when calls are independent.

### 2.2 How

**Single tool.** The model emits one tool call per turn. The application executes it, appends the result, and calls the model again. Terminate when `finish_reason == "stop"`. This is the baseline pattern from `tool-usage.md`.

**Parallel tools.** The model emits multiple tool calls in a single response. The application executes all of them (potentially concurrently), appends one result message per call (each with its own `tool_call_id`), and calls the model once more. The model may emit another set of parallel calls or produce the final response.

The key difference from single-tool: `message.tool_calls` is a list. The application must iterate the list, execute each, and return a result message for every call before the next model invocation.

**Sequential chain.** The application knows in advance that the output of one tool feeds into the next. Rather than letting the model drive each step, the application hard-codes the pipeline: call tool A, extract a field from the result, pass it as the argument to tool B. Each step is a separate API call with an expanding message history.

Sequential chains trade model reasoning for application predictability. They are appropriate when the order of operations is invariant and the intermediate steps are not user-visible.

**Router pattern.** Multiple tools are declared and the model selects which one applies based on the user query. The application does not pre-select the tool; it presents all options and lets the model decide. After the selected tool executes, the model produces the final response.

The router pattern composes with the others: the model may route to a tool and then call a second tool in parallel, or trigger a sequential chain.

### 2.3 Code example

```python
# See: labs/structured-outputs/lab-tool-patterns/main.py

# Parallel tools: handle a list of tool calls in one response
def run_parallel_tools(client, messages, tools):
    response = client.chat.completions.create(
        model="llama3.2", messages=messages, tools=tools
    )
    msg = response.choices[0].message
    # Append the assistant message containing all tool calls
    messages.append(msg)

    if msg.tool_calls:
        for call in msg.tool_calls:
            result = dispatch(call.function.name, call.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
        # One more call after all results are returned
        response = client.chat.completions.create(
            model="llama3.2", messages=messages, tools=tools
        )
    return response.choices[0].message.content


# Sequential chain: hard-coded pipeline
def run_sequential_chain(client, query: str):
    # Step 1: resolve city to coordinates
    coords = call_tool(client, query, "geocode_city")
    # Step 2: fetch weather using coordinates
    weather = call_tool(client, coords["lat"], coords["lon"], "get_weather")
    return weather
```

---

## 3. Table

| Pattern | Tool calls per turn | Model drives selection | API round-trips | Use case |
|---------|--------------------|-----------------------|-----------------|----------|
| Single tool | 1 | Partially (tool_choice=auto) | 2 (call + final) | One capability, one invocation |
| Parallel tools | N (simultaneous) | Yes | 2+ | Multiple independent data sources |
| Sequential chain | 1 per step | No (app-driven) | N+1 | Pipeline with data dependencies |
| Router pattern | 1 (model-selected) | Yes (selects from N tools) | 2 | Dispatching among capabilities |

| Application responsibility | Single | Parallel | Sequential | Router |
|---------------------------|--------|----------|------------|--------|
| Iterate tool_calls list | No | Yes | No | No |
| Execute concurrently | No | Optional | No | No |
| Hard-code step order | No | No | Yes | No |
| Declare all tools upfront | No | Yes | No | Yes |

---

## 4. Engineering Implications

**Parallel execution is an application choice.** The model emits multiple tool calls simultaneously, but the application decides whether to execute them sequentially or concurrently (e.g., with `asyncio.gather` or `ThreadPoolExecutor`). Independent tool calls with high latency — external API calls, database queries — benefit from concurrent execution.

**Sequential chains remove model agency.** By hard-coding the pipeline, the application sacrifices the model's ability to short-circuit, reorder, or skip steps based on intermediate results. This is desirable for invariant pipelines but limits adaptability.

**Router completeness matters.** If the declared tool set does not cover a user's request, the model will either call the closest matching tool incorrectly or produce a text response (ignoring tools). Tool descriptions must be specific enough for the model to distinguish between options and general enough to cover intended use cases.

**Message history grows with each round-trip.** A sequential chain with five steps accumulates five tool call messages and five tool result messages before the final response. This consumes context tokens. In long chains, earlier messages may need to be pruned or summarized to stay within the context window.

**Nested routing.** The router and parallel patterns compose: the model may route to a tool that itself triggers a sequential sub-chain. This is the foundation of multi-step agent loops, covered in the `ai-agents` module.

---

## 5. Implementation Connection

`lab-tool-patterns` implements all four patterns against concrete tools (weather lookup, currency conversion, city geocoding):

1. **Single tool** — baseline from `lab-tool-usage`, included for comparison.
2. **Parallel tools** — a query asking for weather in two cities simultaneously; observe that `tool_calls` contains two entries.
3. **Sequential chain** — geocode a city, then fetch weather using the returned coordinates; observe the message list growing across steps.
4. **Router** — three tools declared; query phrasing determines which tool is selected; run multiple queries and observe model selection behavior.

The lab measures round-trip count per pattern. Note the difference between parallel (2 round-trips regardless of N tools) and sequential (N+1 round-trips).

---

## 6. Failure Modes and Limitations

**Partial parallel execution failure.** If one tool in a parallel set fails, the application must still return a result message for every `tool_call_id` before the model can continue. Returning an error string as the content is acceptable; omitting the result message causes the model to stall or produce an error.

**Router misclassification.** The model may select the wrong tool when descriptions overlap or the query is ambiguous. This is a prompt-quality and schema-design problem — tighten tool descriptions and add discriminating examples in the `description` field.

**Context exhaustion in long chains.** Each step in a sequential chain adds messages to the history. A chain of ten steps with verbose results can exhaust a 4K context window. Summarize or truncate intermediate results when building long pipelines.

**Parallel call count is model-dependent.** Not all models emit multiple tool calls in a single turn. Some models emit one call even when parallel execution is possible. Test the specific model against parallel scenarios before relying on this behavior in production.

---

## 7. Summary

Four patterns cover the composition space for tool use: single tool for isolated capability, parallel tools for independent concurrent needs, sequential chain for hard-coded pipelines, and router for model-driven dispatch. Each has a distinct message accumulation strategy and a different trade-off between model agency and application control. Recognizing the pattern determines the loop structure before writing code.
