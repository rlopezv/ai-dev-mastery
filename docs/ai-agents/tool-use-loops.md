---
id: "ai-agents-tool-use-loops"
title: "Tool-Use Loops"
type: "topic"
step: "ai-agents"
path: "docs/ai-agents/tool-use-loops.md"
status: "draft"
level: "intermediate"

concepts:
  - "tool-use loop"
  - "tool result accumulation"
  - "multi-turn tool use"

prerequisites:
  - "docs/ai-agents/single-agent-loop.md"
  - "docs/structured-outputs/tool-patterns.md"

next:
  - "docs/ai-agents/multi-agent-systems.md"

related:
  - "docs/structured-outputs/tool-usage.md"
  - "docs/memory-context/conversation-history.md"

implementation_refs:
  - "labs/ai-agents/lab-tool-use-loops"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how tool calls and results accumulate in the message history, how parallel and sequential tool patterns extend the basic loop, and how the loop terminates cleanly."
---

## 1. Intuition

A tool-use loop is a conversation in which one of the participants is a tool. The message
history grows with each exchange: user message, assistant tool call, tool result, assistant
tool call, tool result, ..., final answer. The LLM sees this history on every call and uses
it to decide what to do next. Understanding how this history is structured is what
distinguishes a working agent from one that fails on the second tool call.

---

## 2. Explanation

### 2.1 Why

The `structured-outputs` module covers single-turn tool use: the model emits one tool call,
the application executes it, and the result is processed by application code — not
re-injected into a conversation. The agent model requires something different: the tool
result must go back to the LLM so that the LLM can reason over it and decide on the next
action.

This creates a specific message accumulation protocol. Getting it wrong — wrong role,
missing `tool_call_id`, wrong message ordering — causes the API to reject the request or
the model to produce inconsistent output. The protocol is precise: every tool call must be
matched by a tool result with the same `tool_call_id`, appended before the next LLM call.

### 2.2 How

The tool-use loop message accumulation follows four rules:

**Rule 1: Append the assistant message before appending tool results.**
When the model emits a message containing tool calls, that message must be appended to the
history as-is (role: `assistant`) before any tool results are added. The tool results are
then appended as role: `tool` messages.

**Rule 2: One result message per tool call.**
If the model emits N tool calls in a single turn (parallel tools), N result messages must
be appended, each matching the `tool_call_id` of its originating call. Missing or mismatched
IDs cause API validation errors.

**Rule 3: All results must be appended before calling the model again.**
After executing all tool calls in a turn, the full set of results is appended before the
next LLM call. The model receives the complete picture of what was executed and what was
returned.

**Rule 4: The loop terminates when finish_reason is "stop".**
A `finish_reason` of `"tool_calls"` signals that more tool calls are pending. A
`finish_reason` of `"stop"` signals that the model has produced a final text response and
no further tool calls are needed.

```text
messages = [system, user_message]

Iteration 1:
  response = llm(messages)           # finish_reason: "tool_calls"
  messages.append(assistant_message) # contains tool_calls
  for each tool_call:
    result = dispatch(tool_call)
    messages.append(tool_result)     # role: "tool", tool_call_id matches

Iteration 2:
  response = llm(messages)           # finish_reason: "stop"
  messages.append(assistant_message) # contains final text response
  return final_text
```

### 2.3 Code example

```python
# See: labs/ai-agents/lab-tool-use-loops/main.py

def run_tool_loop(client, tools, messages, max_iterations=10):
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL, tools=tools, messages=messages
        )
        msg = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [tc.model_dump() for tc in (msg.tool_calls or [])],
        })
        if response.choices[0].finish_reason == "stop":
            return msg.content
        for tc in msg.tool_calls:
            result = dispatch(tc)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            })
    return "Max iterations reached."
```

---

## 3. Message Accumulation Protocol

| Event | Message role | Key fields |
|-------|-------------|------------|
| Model emits tool calls | `assistant` | `tool_calls` list with `id`, function name, arguments |
| Tool executes | `tool` | `tool_call_id` (must match call `id`), `content` (result string) |
| Model emits final answer | `assistant` | `content` (text), no `tool_calls` |
| Parallel tool calls | N × `tool` | One result per call, all appended before next LLM call |

---

## 4. Engineering Implications

**Parallel tool calls reduce loop iterations but require all results before re-calling.**
When the model emits multiple tool calls in one turn, they can be dispatched concurrently
(since they are independent by declaration). All results must be appended before the next
LLM call — partially appending results causes the model to reason over an incomplete state.

**Tool result content must be a string.** LLM APIs require the `content` field of tool
result messages to be a string. If the tool returns a structured object, it must be
serialized to a JSON string before appending. Passing a raw dict causes an API validation
error.

**History length grows O(iterations × tools_per_turn).** Each iteration adds at least two
messages (one assistant with tool calls, one or more tool results). At 10 iterations with 3
parallel tool calls per iteration, the history grows by 40 messages per run. Combined with
potentially verbose tool outputs, this is the primary token budget risk in tool-heavy agents.

**Finish reason "length" is a budget failure, not a stop condition.** If `finish_reason` is
`"length"`, the model ran out of output tokens before completing its response. In agentic
contexts this typically means a tool result was too large and the model could not produce a
complete tool call. The response must be treated as failed, not successful.

---

## 5. Implementation Connection

`lab-tool-use-loops` implements the accumulation protocol with three tools — a calculator,
a web search stub, and a file reader. It deliberately exercises parallel tool dispatch (the
model calls calculator and search in the same turn) and sequential dependency (the file
reader is called after search returns a file path). Both the message history and the
per-iteration token count are printed, making the accumulation and budget consumption
visible.

---

## 6. Failure Modes and Limitations

**Missing tool_call_id in result.** If the `tool_call_id` in a tool result message does not
match any pending tool call in the assistant message, the API returns a validation error.
This happens when the dispatcher serializes the call object incorrectly or when the loop
skips appending the assistant message before the results.

**Partial result append.** In a parallel tool call with N tools, if the application appends
fewer than N results before calling the model again, the model sees an incomplete state and
may repeat calls that were already executed or produce inconsistent reasoning.

**Unbounded tool output.** A tool that returns the full contents of a large document on
every call will exhaust the context window within a few iterations. Tool outputs must be
bounded — by character count, by pagination, or by returning summaries instead of raw
content.

---

## 7. Summary

The tool-use loop governs how tool calls and results accumulate in the message history. The
protocol is strict: append the assistant message before the results, append one result per
tool call with the matching `tool_call_id`, append all results before re-calling the model,
and terminate on `finish_reason == "stop"`. Violations cause API errors or inconsistent
model behavior. Correct accumulation is what allows the LLM to reason across multiple tool
interactions as a coherent conversation rather than a sequence of isolated calls.
