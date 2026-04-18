---
id: "ai-agents-agent-patterns"
title: "Agent Patterns"
type: "topic"
step: "ai-agents"
path: "docs/ai-agents/agent-patterns.md"
status: "draft"
level: "intermediate"

concepts:
  - "ReAct pattern"
  - "plan-and-execute"
  - "reflection"

prerequisites:
  - "docs/ai-agents/tool-use-loops.md"

next:
  - "docs/ai-agents/mcp.md"

related:
  - "docs/ai-agents/multi-agent-systems.md"
  - "docs/prompt-engineering/chain-of-thought.md"

implementation_refs:
  - "labs/ai-agents/lab-agent-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes three reusable agent patterns — ReAct, plan-and-execute, and reflection — and the conditions under which each is the right structural choice."
---

# Agent Patterns

## Navigation

[Docs](../README.md) / [AI Agents](README.md) / Agent Patterns

---

## 1. Intuition

A raw agent loop — perceive, decide, act — works for simple tasks but produces opaque and
brittle behavior on complex ones. Agent patterns are structural solutions to recurring
failure modes: agents that act without reasoning, agents that cannot recover from unexpected
results, agents that produce outputs they have not verified. Each pattern adds structure to
the loop to make it more predictable, traceable, and robust.

---

## 2. Explanation

### 2.1 Why

An unstructured agent loop gives the model maximum freedom — it can call any tool at any
time with any reasoning it chooses. This freedom is a liability for complex tasks:

- A model that does not externalize its reasoning may make inconsistent decisions across
  iterations, especially in long loops where early context is diluted.
- A model that commits to a plan in iteration 1 and encounters a blocking result in
  iteration 3 has no mechanism to re-plan — it will either force through the original plan
  or improvise inconsistently.
- A model that generates a final answer does not, by default, evaluate that answer before
  returning it. Errors, hallucinations, and constraint violations pass through unchecked.

Patterns address each failure mode by adding an explicit structural step to the loop.

### 2.2 How

**ReAct (Reasoning + Acting)** interleaves explicit reasoning steps with action steps.
Before each tool call, the model produces a "Thought" — a brief statement of what it knows,
what it needs, and why it is calling this specific tool. After the tool returns, the model
produces a new "Thought" interpreting the result. The alternation
Thought → Action → Observation → Thought creates a traceable chain of reasoning visible in
the message history.

ReAct is implemented through the system prompt: the model is instructed to output
`Thought: ...` before every `Action: ...`. The dispatcher parses and executes the action;
the result is appended as `Observation: ...`. This structure is not a new loop — it is the
same loop with an enriched output format.

**Plan-and-execute** separates planning from execution into two phases:

*Planning phase:* The model receives the task and produces a structured plan — a list of
steps with expected inputs, expected outputs, and tool assignments — without executing any
tools. The plan is stored and passed to the execution phase.

*Execution phase:* The executor agent works through the plan step by step. When a step
fails, the executor passes the failure back to the planner, which revises the remaining
steps. Planning and execution alternate until the task is complete or a stop condition is
reached.

The separation of concerns is the value: the planner reasons about the task structure
without the noise of tool outputs; the executor works through the steps without the overhead
of global task reasoning.

**Reflection** adds a post-generation evaluation step: after the agent produces a draft
output, a second LLM call (the reflector) evaluates the draft against the original task,
checking for factual consistency, constraint satisfaction, and completeness. The reflector
produces an assessment with specific corrections; the generator revises and re-reflects
until the reflector approves or a revision ceiling is reached.

Reflection can be implemented with the same model (self-reflection) or a different model
(external judge). Self-reflection is cheaper but has the same failure modes as the original
generation. An external judge is more reliable but doubles LLM call count.

### 2.3 Code example

```python
# See: labs/ai-agents/lab-agent-patterns/main.py

# ReAct: system prompt that enforces thought-action-observation structure
REACT_SYSTEM = """
You must follow this format for every step:
Thought: [what you know and what you need]
Action: [tool name] [arguments as JSON]
Observation: [provided by the system after tool execution]
...
Final Answer: [your answer when done]
"""

# Reflection: two-call cycle with revision ceiling
def reflect_and_revise(client, task, draft_answer, max_revisions=3):
    for _ in range(max_revisions):
        reflection = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Evaluate the answer against the task. "
                 "Reply APPROVED if correct, or list specific issues."},
                {"role": "user", "content": f"Task: {task}\nAnswer: {draft_answer}"},
            ]
        ).choices[0].message.content
        if "APPROVED" in reflection:
            return draft_answer
        draft_answer = revise(client, task, draft_answer, reflection)
    return draft_answer
```

---

## 3. Pattern Comparison

| Pattern | Adds to loop | Solves | Cost |
|---------|-------------|--------|------|
| ReAct | Explicit reasoning traces | Opaque decisions, hard-to-debug loops | Slightly more tokens per iteration |
| Plan-and-execute | Separate plan + re-plan phases | Inability to recover from unexpected results | Extra LLM calls for planning and re-planning |
| Reflection | Post-generation evaluation step | Unverified output quality | 1–3 extra LLM calls per final answer |

---

## 4. Engineering Implications

**ReAct improves debuggability at low cost.** The Thought traces appear in the message
history and can be logged, monitored, and analyzed. An agent that fails can be diagnosed by
reading the Thought sequence — the reasoning breakdown is explicit, not inferred.

**Plan-and-execute is not worth the overhead for short tasks.** The planning phase adds a
full LLM call that produces no observable output. For tasks that complete in two or three
tool calls, plan-and-execute adds latency without benefit. Reserve it for tasks with more
than five steps or tasks where failure recovery is critical.

**Reflection introduces a revision loop that must be capped.** Without a revision ceiling,
a reflector that consistently finds issues will cycle indefinitely. The revision ceiling is a
hard stop — not a quality target. Set it to 2–3 revisions: if the answer is not acceptable
after three revisions, the task prompt or the tools need fixing, not more revisions.

**Patterns compose.** A plan-and-execute agent can use ReAct in its execution phase for
traceable step execution. A reflection step can follow a ReAct loop for final answer
verification. Compositions of patterns should be introduced incrementally — add one pattern
at a time and measure the improvement.

---

## 5. Implementation Connection

`lab-agent-patterns` implements all three patterns on a common agent base. The lab runs the
same multi-step research task through an unstructured loop, a ReAct loop, and a
plan-and-execute loop, comparing the message traces and final answers. Reflection is applied
as a post-processing step on the final answer from each pattern. The lab makes the structural
difference between patterns directly observable in the message history.

---

## 6. Failure Modes and Limitations

**ReAct thought parsing fragility.** If the model deviates from the Thought/Action/Observation
format — which happens under high context pressure — the dispatcher cannot parse the action.
The system prompt must be reinforced and the parser must handle format violations gracefully,
logging the deviation and prompting the model to reformat.

**Plan staleness in plan-and-execute.** If the plan is generated at the start and never
revised, a tool failure in step 3 may make all remaining steps invalid. The re-planning
mechanism must be triggered by explicit failure signals from the executor, not left optional.

**Reflection hallucination.** A reflector that is given only the draft answer and the task
may approve an incorrect answer if it cannot independently verify the facts. Reflection
catches formatting and consistency errors reliably; it does not substitute for tool-verified
factual accuracy.

---

## 7. Summary

Agent patterns add structure to the basic loop to address specific failure modes: ReAct makes
reasoning visible and debuggable, plan-and-execute enables recovery from unexpected results by
separating task decomposition from execution, and reflection verifies output quality before it
reaches the user. Each pattern introduces extra LLM calls or additional prompt structure — the
trade-off is reliability and observability at the cost of latency and token consumption.
Patterns are selected by failure mode, not by preference: apply the simplest pattern that
solves the specific reliability problem being encountered.
