---
id: "ai-agents-single-agent-loop"
title: "The Single-Agent Loop"
type: "topic"
step: "ai-agents"
path: "docs/ai-agents/single-agent-loop.md"
status: "draft"
level: "intermediate"

concepts:
  - "single-agent loop"
  - "stop condition"
  - "action dispatcher"

prerequisites:
  - "docs/ai-agents/agent-fundamentals.md"

next:
  - "docs/ai-agents/tool-use-loops.md"

related:
  - "docs/structured-outputs/tool-usage.md"
  - "docs/structured-outputs/tool-patterns.md"

implementation_refs:
  - "labs/ai-agents/lab-single-agent-loop"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains the single-agent loop structure: how a single LLM drives a perception-decide-act cycle with tool dispatch until a stop condition terminates the loop."
---

# The Single-Agent Loop

## Navigation

[Docs](../README.md) / [AI Agents](README.md) / The Single-Agent Loop

---

## 1. Intuition

The single-agent loop is the simplest possible agent: one LLM, one set of tools, and a loop
that runs until the LLM says it is done. Every more complex agent — multi-step pipelines,
multi-agent systems, MCP-connected tools — is an extension of this structure. Understanding
the single-agent loop means understanding the foundation.

---

## 2. Explanation

### 2.1 Why

The single-tool and parallel-tool patterns from `structured-outputs` are static: the
application decides in advance how many tool calls to make. The single-agent loop removes
that constraint. The LLM decides how many tool calls the task requires, in what order, and
with what arguments — all based on what it observes during execution.

This dynamic control enables tasks that cannot be decomposed in advance: "find the three
most relevant articles about X and summarize the points they disagree on" requires an
unknown number of search calls, filtering decisions, and summary generations, all dependent
on what the search results actually contain.

### 2.2 How

The single-agent loop has four components that operate together:

**Tool registry** — the set of tools declared in the API request. Each tool has a name, a
description, and a JSON Schema for its parameters. The LLM reads descriptions to decide
which tool to call and when.

**Action dispatcher** — the application-side function that receives a tool call from the
model response, routes it to the correct function implementation, executes it, and returns
the result. The dispatcher is the bridge between the model's decisions and the runtime
environment.

**Message accumulator** — the growing list of messages passed to the LLM on each iteration.
Every tool call and tool result is appended before the next call. The accumulator is the
agent's working memory — it contains the full history of the current task.

**Stop condition** — the check that terminates the loop. Primary: `finish_reason == "stop"`
from the API response (the model emits a text response with no tool calls). Secondary: a
maximum iteration ceiling enforced by the application regardless of the model's output.

```text
Application                  LLM
─────────                    ───
messages ──────────────────► perceive
                             decide ──────────► tool call or stop
         ◄──── tool call
dispatch(tool_call) → result
messages.append(result)
messages ──────────────────► perceive (next iteration)
...
                             decide ──────────► stop
         ◄──── text response
return response
```

### 2.3 Code example

```python
# See: labs/ai-agents/lab-single-agent-loop/main.py

def dispatch(tool_call) -> str:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    if name == "search_web":
        return search_web(**args)
    if name == "read_document":
        return read_document(**args)
    return f"Unknown tool: {name}"

def run_agent(client, tools, system_prompt, user_message, max_iterations=10):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL, tools=tools, messages=messages
        )
        msg = response.choices[0].message
        messages.append(msg)
        if response.choices[0].finish_reason == "stop":
            return msg.content
        for tc in msg.tool_calls:
            result = dispatch(tc)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
    return "Max iterations reached."
```

---

## 3. Loop Component Breakdown

| Component | Role | Location |
|-----------|------|----------|
| Tool registry | Declares available tools with descriptions and schemas | API request (`tools=` parameter) |
| Action dispatcher | Routes tool calls to implementations and returns results | Application code |
| Message accumulator | Maintains the full history of the current task | Application state (list of messages) |
| Stop condition | Terminates the loop when the task is complete or ceiling is reached | Application code (`finish_reason` check + ceiling) |

---

## 4. Engineering Implications

**Tool descriptions drive dispatch quality.** The LLM selects tools based on their
descriptions. A description that does not distinguish two similar tools will cause the wrong
tool to be called. Tool names and descriptions must be unambiguous — they are read by the
model, not just by developers.

**Dispatcher errors must be returned as tool results, not raised as exceptions.** If a tool
call fails — wrong arguments, network error, resource not found — the result must be
appended to the message history as an error string. Raising an exception instead breaks the
loop without giving the LLM an opportunity to recover or retry.

**The message accumulator is bounded by the context window.** Each loop iteration adds
messages. A tool that returns long documents can exhaust the context window in two or three
iterations. Tool outputs must be constrained — by truncation, summarization, or pagination —
to keep the accumulator within budget.

**Iteration ceiling is a safety control, not a performance setting.** A ceiling of 10 does
not mean the agent is expected to run 10 iterations. It means that after 10 iterations, the
application stops regardless of the model's state. The ceiling should be set to the maximum
plausible task length plus a safety margin, not tuned downward to save compute.

---

## 5. Implementation Connection

`lab-single-agent-loop` builds the complete loop: tool registry, action dispatcher, message
accumulator, and stop condition. The lab uses two tools — a web search stub and a document
reader — to demonstrate an agent completing a multi-step research task. The iteration count
and accumulated messages are printed at each step, making the loop's progression observable.

---

## 6. Failure Modes and Limitations

**Dispatcher-model schema mismatch.** If the dispatcher's function signature changes without
updating the tool declaration's JSON Schema, the model will pass valid-looking arguments
that the function cannot accept. The schema and the function must be kept in sync.

**Runaway accumulation.** A loop that runs the maximum number of iterations will accumulate
`max_iterations × 2` messages (one tool call + one tool result per iteration) plus the
original messages. At 10 iterations with 1,000-token tool outputs, the accumulator holds
20,000+ tokens before the final response is generated. Token budget planning must account
for worst-case accumulation.

**Tool call format regression.** Some model versions produce malformed tool calls under
certain conditions — empty argument objects, incorrectly quoted strings, missing required
fields. The dispatcher must validate the `arguments` field before calling `json.loads()`.

---

## 7. Summary

The single-agent loop combines a tool registry, an action dispatcher, a message accumulator,
and a stop condition into a structure where the LLM drives multi-step task execution. The
application executes what the model requests and returns results; the model decides what to
request next. The loop terminates when the model emits a stop response or the iteration
ceiling is reached. This structure is the foundation for every more complex agent design —
understanding it means understanding every pattern built on top of it.
