---
id: "ai-agents-agent-fundamentals"
title: "Agent Fundamentals"
type: "topic"
step: "ai-agents"
path: "docs/ai-agents/agent-fundamentals.md"
status: "draft"
level: "intermediate"

concepts:
  - "agent loop"
  - "agentic application"
  - "autonomy"
  - "stop condition"

prerequisites:
  - "docs/structured-outputs/tool-usage.md"
  - "docs/memory-context/README.md"

next:
  - "docs/ai-agents/single-agent-loop.md"

related:
  - "docs/structured-outputs/tool-patterns.md"
  - "docs/ai-agents/agent-patterns.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Defines the agent model, distinguishes agents from single-turn LLM calls, and explains why the loop structure is the minimal unit of agentic behavior."
---

## 1. Intuition

A single LLM call is a function: input in, output out, no memory of what happened before
and no ability to take further action. An agent is different: it receives a task, decides
whether to act or respond, acts (calls a tool), observes the result, and decides again. The
loop runs until the task is complete. The loop is what makes it an agent.

---

## 2. Explanation

### 2.1 Why

Single-turn LLM calls cannot solve problems that require sequential decisions, tool
interaction, or state that accumulates across steps. A task like "fetch the current price
of AAPL, compare it to last week's price, and report the percentage change" requires at
least two tool calls in sequence, where the second depends on the result of the first. No
single API call can do this — the application must orchestrate the steps.

The agent model addresses this by giving the LLM control over when the work is done. Instead
of the application calling the LLM once and processing the result, the LLM calls tools,
observes their results, and continues until it has enough information to produce a final
answer. The application's job becomes executing what the LLM requests and returning the
results — not deciding what to do next.

### 2.2 How

The agent loop has three phases that repeat until a stop condition is reached:

**Perceive** — the agent reads its current state: the original task in the system prompt,
the conversation history, and the results of any tools already executed. This is its full
view of the world.

**Decide** — the agent produces one of two outputs: a tool call (specifying which tool to
invoke and with what arguments), or a final response (when no further tool calls are needed).
The decision is implicit — the model emits a tool call when it determines that more
information or action is needed, and emits a text response when it is ready to answer.

**Act** — the application executes the tool call and appends the result to the conversation.
Control returns to the model for the next perception phase.

**Stop condition** — the loop terminates when the model emits a response with
`finish_reason == "stop"` (no tool call in the output) or when a safety ceiling is reached
(maximum iteration count). The stop condition is enforced by the application, not the model.

The critical property is that the LLM drives control flow. The application does not know in
advance how many tool calls the agent will make or which tools it will use. This is what
distinguishes an agent from a sequential chain of predetermined API calls.

### 2.3 Code example

```python
# See: labs/ai-agents/lab-single-agent-loop/main.py

def run_agent(client, tools, messages, max_iterations=10):
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL,
            tools=tools,
            messages=messages
        )
        choice = response.choices[0]
        if choice.finish_reason == "stop":
            return choice.message.content     # final answer — loop terminates
        # tool call — execute and append result before next iteration
        messages = handle_tool_calls(messages, choice.message)
    return "Maximum iterations reached."
```

---

## 3. Agent vs. Non-Agent Comparison

| Property | Single-turn call | Agent loop |
|----------|-----------------|------------|
| Number of LLM calls | 1 | 1 to N |
| Tool invocation | None or 1 (structured outputs) | 0 to N per iteration |
| Control flow driver | Application | LLM |
| Stop condition | Always after 1 call | When LLM emits stop or ceiling reached |
| Task types | Single-step, self-contained | Multi-step, conditional, sequential |
| Memory across steps | None (application-managed) | Conversation history accumulation |

---

## 4. Engineering Implications

**Unbounded execution is a design risk.** Because the agent decides when to stop, a poorly
constrained prompt or unexpected tool behavior can cause the loop to run indefinitely. Every
agent loop must have a maximum iteration ceiling enforced by the application.

**Tool quality determines agent quality.** The LLM can only decide as well as the tools it
can call. A tool with an ambiguous description will be invoked with wrong arguments. A tool
that returns unstructured text forces the model to parse it before reasoning over it. Tool
design is as important as prompt design in agent systems.

**Latency compounds per iteration.** Each loop iteration adds at least one LLM call plus one
tool execution. An agent that runs three iterations has 3× the latency of a single-turn call,
plus tool execution overhead. Long tool chains must be designed with latency budgets in mind.

**Conversation history grows with each iteration.** Every tool call and result is appended to
the message list. A ten-step agent loop with verbose tool outputs can consume tens of
thousands of tokens before producing a final answer. Token budget management from
`memory-context` applies directly here.

---

## 5. Implementation Connection

`lab-single-agent-loop` implements the minimal viable agent: one LLM, one tool set, a loop
with a stop condition and a maximum iteration ceiling. The lab makes the
perception-decide-act cycle observable by printing each iteration's decision and the
resulting tool output before the loop continues.

This document has no direct lab because it is concept-only — the implementation starts in
`single-agent-loop.md`.

---

## 6. Failure Modes and Limitations

**Infinite loops without a ceiling.** If the model is given a task it cannot complete with
the available tools, it may continue emitting tool calls indefinitely — querying different
combinations, retrying failed calls, or calling tools in circles. The iteration ceiling is
the only protection.

**Tool call hallucination.** The model may invoke tools that do not exist or pass arguments
that do not match the tool's schema. Both are caught at dispatch time, but they require error
handling in the tool result message to allow the loop to recover.

**Irreversible actions without confirmation.** An agent that can call write-side tools
(delete, send, publish) may take irreversible actions based on a misunderstood task.
Production agents should implement a confirmation step before any destructive tool call.

**Single-agent bottleneck.** A single agent processes tool calls sequentially. Tasks that
require many independent sub-tasks benefit from parallel multi-agent delegation — a pattern
covered in `multi-agent-systems.md`.

---

## 7. Summary

An agent is an LLM in a loop: it perceives the current state, decides on an action (tool
call or final answer), and acts until a stop condition is met. The loop is the minimal unit
of agentic behavior — without it, the LLM cannot execute multi-step tasks that depend on
intermediate results. The application drives execution (calling the LLM, running tools) but
does not control the decision sequence — the LLM does. This inversion of control is the
defining property of the agent model and the source of both its power and its engineering
risks.
