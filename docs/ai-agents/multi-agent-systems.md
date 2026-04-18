---
id: "ai-agents-multi-agent-systems"
title: "Multi-Agent Systems"
type: "topic"
step: "ai-agents"
path: "docs/ai-agents/multi-agent-systems.md"
status: "draft"
level: "intermediate"

concepts:
  - "multi-agent systems"
  - "orchestrator"
  - "subagent"

prerequisites:
  - "docs/ai-agents/tool-use-loops.md"

next:
  - "docs/ai-agents/agent-patterns.md"

related:
  - "docs/ai-agents/agent-fundamentals.md"
  - "docs/ai-agents/architecture.md"

implementation_refs:
  - "labs/ai-agents/lab-multi-agent"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains why complex tasks require multiple agents, how orchestrators decompose and delegate work to subagents, and the trade-offs between centralized and distributed agent control."
---

# Multi-Agent Systems

## Navigation

[Docs](../README.md) / [AI Agents](README.md) / Multi-Agent Systems

---

## 1. Intuition

A single agent with ten tools is hard to reason about — the model must decide among ten
options at every step, tools interfere with each other conceptually, and the context window
fills with the outputs of all ten. Two agents, each with five specialized tools and a clear
mandate, are easier to control, test, and debug. A multi-agent system partitions complexity
by giving each agent a scope it can manage.

---

## 2. Explanation

### 2.1 Why

A single-agent loop works well for tasks that are sequential and contained — the agent makes
tool calls, accumulates results, and produces one answer. It breaks down when:

- **Tasks have independent sub-tasks that can run in parallel.** "Summarize the latest news
  from three different sources" requires three independent retrieval + summarize operations.
  A single agent executes them sequentially; three subagents execute them concurrently.

- **Specialization improves quality.** A coding agent with access to a code execution tool
  and a test runner produces better results than a general agent that also has access to a
  search tool, a calculator, and a document reader. Restricting the tool set sharpens the
  model's decision space.

- **Tasks exceed the context window.** A single agent accumulating the results of twenty
  tool calls will exhaust a 128k context window. A coordinator that delegates sub-tasks to
  subagents and receives summaries — not raw outputs — keeps its own context bounded.

Multi-agent systems solve these problems by splitting both the tool set and the context
budget across agents.

### 2.2 How

A multi-agent system has two roles:

**Orchestrator** — the coordinating agent that receives the original task, decomposes it
into sub-tasks, invokes subagents (as tools), and aggregates their results into a final
response. The orchestrator does not execute domain tools directly; it delegates. Its tool
set consists of subagent invocation functions.

**Subagent** — a specialized agent with a narrow tool set and a specific mandate. It
receives a sub-task, executes it through its own internal loop, and returns a result to the
orchestrator. The subagent has no knowledge of the orchestrator's full task or of other
subagents.

The message passing protocol is identical to the tool-use loop: the orchestrator emits a
tool call (invoking a subagent), the subagent function runs its own loop internally, and
the result is appended as a tool result before the orchestrator's next iteration.

```text
Orchestrator receives: "Research X from three sources and write a comparison."

Iteration 1 (orchestrator):
  Calls: research_agent(query="X", source="arxiv")
         research_agent(query="X", source="news")
         research_agent(query="X", source="blogs")

  Each research_agent call:
    Runs its own loop: search → filter → summarize → return summary

Iteration 2 (orchestrator):
  Receives three summaries
  Writes comparison → final answer
```

### 2.3 Code example

```python
# See: labs/ai-agents/lab-multi-agent/main.py

def research_agent(query: str, source: str) -> str:
    """Subagent: searches a specific source and returns a summary."""
    tools = [search_tool(source=source), summarize_tool()]
    messages = [
        {"role": "system", "content": f"You are a research agent. Search {source} and summarize."},
        {"role": "user", "content": query},
    ]
    return run_agent(client, tools, messages)  # internal loop

def run_orchestrator(query: str) -> str:
    orchestrator_tools = [
        make_tool("research_agent", research_agent, params=["query", "source"])
    ]
    messages = [
        {"role": "system", "content": "You coordinate research across multiple sources."},
        {"role": "user", "content": query},
    ]
    return run_agent(client, orchestrator_tools, messages)  # outer loop
```

---

## 3. Multi-Agent Topology Comparison

| Topology | Structure | When to use |
|----------|-----------|-------------|
| Orchestrator + subagents | One coordinator, N specialized workers | Tasks with independent sub-tasks or specialist delegation |
| Pipeline | Sequential agents, each processing the previous output | Tasks with strict stage dependencies (retrieve → filter → generate) |
| Peer-to-peer | Agents communicate directly without a coordinator | Debate and critique tasks (agent A proposes, agent B critiques) |
| Hierarchical | Orchestrator with sub-orchestrators | Very large tasks requiring multiple levels of decomposition |

---

## 4. Engineering Implications

**Subagent results must be summarized, not passed raw.** If a subagent returns the full
content of a retrieved document, the orchestrator's context fills with raw data rather than
processed intelligence. Subagents should return structured summaries that the orchestrator
can reason over without reading every token.

**Parallel subagent invocation is only safe for independent tasks.** Subagents can be
dispatched in parallel (as parallel tool calls from the orchestrator) only if their tasks
are truly independent — no shared state, no ordering dependency. If subagent B's task
depends on subagent A's output, they must be sequential.

**Context isolation is a feature, not a limitation.** The fact that each subagent sees only
its own task — not the orchestrator's full context — prevents context contamination. A
subagent specialized in code review should not see the conversational history of the user's
broader session. Context isolation enforces clean separation of concerns.

**Error propagation requires explicit design.** If a subagent fails (network error, tool
exception, no useful result), the orchestrator receives its error message as a tool result.
The orchestrator must be designed to handle partial results — to proceed with available data
or to retry the failed subagent — rather than silently producing an incomplete answer.

---

## 5. Implementation Connection

`lab-multi-agent` builds a two-level system: an orchestrator that decomposes a research task
into parallel sub-tasks, and a research subagent that executes each sub-task through its own
loop. The lab measures orchestrator context size with and without subagent result
summarization, demonstrating the token budget difference. The subagent's internal loop is
identical to `lab-single-agent-loop` — multi-agent is not a new primitive but a composition
of the same loop at multiple levels.

---

## 6. Failure Modes and Limitations

**Orchestrator overreach.** An orchestrator that performs domain work in addition to
coordinating (searching, summarizing, calculating) degrades into a single-agent loop with
extra complexity. The orchestrator's role must be strictly coordination — no direct domain
tool calls.

**Subagent context leakage.** If the subagent is initialized with the orchestrator's full
message history (instead of just its sub-task), context isolation is lost. Subagents must
receive a fresh, scoped message list containing only what is needed for the sub-task.

**Debugging opacity.** In a single-agent loop, the full execution trace is visible in the
message history. In a multi-agent system, the subagent's internal trace is invisible to the
orchestrator — it sees only the result. Observability requires explicit logging inside each
subagent's loop.

**Cascading failure.** If an orchestrator calls subagents sequentially and the first
subagent fails, the orchestrator must decide how to proceed before calling the second.
Without explicit failure handling, the orchestrator may propagate the error through all
downstream subagents before returning an incomplete result.

---

## 7. Summary

Multi-agent systems partition complex tasks across specialized agents connected by a
coordination protocol. The orchestrator decomposes, delegates, and aggregates — it does not
execute domain work. Subagents execute domain work in their own isolated loops and return
results. The protocol between orchestrator and subagent is the same tool-use loop used in
single-agent systems: subagent invocations are tool calls, subagent results are tool
results. The benefit is scope control: each agent has a bounded tool set, a bounded context,
and a bounded responsibility — the properties that make agent behavior testable and
predictable.
