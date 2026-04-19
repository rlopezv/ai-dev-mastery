---
id: "ai-agents-architecture"
title: "AI Agents — Architecture"
type: "architecture"
step: "ai-agents"
path: "docs/ai-agents/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "agent loop"
  - "action dispatcher"
  - "orchestrator"
  - "subagent"
  - "MCP server"
  - "tool registry"

prerequisites:
  - "docs/ai-agents/README.md"
  - "docs/ai-agents/mcp.md"

next:
  - "docs/ai-agents/implementation-reference.md"

related:
  - "docs/ai-agents/multi-agent-systems.md"
  - "docs/ai-agents/agent-patterns.md"
  - "docs/structured-outputs/tool-usage.md"

implementation_refs:
  - "labs/ai-agents/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the component architecture of an agentic system: the single-agent loop, multi-agent topology, and MCP server integration as composable layers."
---

# AI Agents — Architecture

## Navigation

[Docs](../README.md) / [AI Agents](README.md) / AI Agents — Architecture

---

## 1. System Overview

An agentic system is an application in which an LLM drives control flow through a series of
tool calls and decisions. The architecture has three composable layers:

1. **Single-agent loop** — the execution unit: one LLM, one tool registry, one action
   dispatcher, one message accumulator, and a stop condition.
2. **Multi-agent topology** — the coordination layer: one or more orchestrators with
   subagent pools, connected by the same tool-use loop protocol used at the single-agent
   level.
3. **MCP integration** — the tool connectivity layer: MCP servers that expose tools to
   agents via a standard protocol, decoupling tool definitions from agent configuration.

These layers are independent. A single-agent loop can use MCP tools. A multi-agent system
can operate entirely with inline tool dispatchers. The layers compose when the problem
requires them, not by default.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| LLM | Decision engine | Produces tool calls or final responses based on current message history |
| Tool registry | Tool catalog | Holds tool declarations (name, description, JSON Schema) passed to the API |
| Action dispatcher | Execution router | Routes tool calls from the model to registered function implementations |
| Message accumulator | Working memory | Maintains the ordered list of messages including tool calls and results |
| Stop condition | Loop terminator | Detects `finish_reason == "stop"` or enforces iteration ceiling |
| Orchestrator | Coordinator | Decomposes tasks, invokes subagents, aggregates results |
| Subagent | Specialist | Executes a scoped sub-task in its own isolated loop |
| MCP client | Protocol adapter | Connects to MCP server, translates discovered tools to API format |
| MCP server | Tool provider | Exposes tools via MCP protocol; handles tool execution |

---

## 3. Component Interactions

At the single-agent level, interactions are synchronous and sequential within each iteration:

```text
LLM ──tool_call──► Action Dispatcher ──execute──► Tool Implementation
                                    ◄──result────
LLM ◄──appended── Message Accumulator
```

At the multi-agent level, the orchestrator's action dispatcher routes calls to subagent
runner functions rather than domain tools:

```text
Orchestrator ──subagent_call──► Subagent Runner
                                │  runs own loop
                                │  tool calls → domain tools
                               ◄──result (summary)
Orchestrator Message Accumulator ◄── appended
```

When MCP is used, the action dispatcher is replaced by the MCP client:

```text
LLM ──tool_call──► MCP Client ──tools/call──► MCP Server ──execute──► Tool
                             ◄──────────────────result────────────────
LLM ◄──appended── Message Accumulator
```

---

## 4. Data Flow

```text
User task
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  Agent Loop                                               │
│                                                           │
│  Messages [system, user] ──────────────────────► LLM     │
│                                                    │      │
│                                    tool_call or stop      │
│                                              │    │      │
│                          ┌───────────────────┘    │      │
│                          ▼                        │      │
│              ┌────────────────────────┐           │      │
│              │   Action Dispatcher    │           │      │
│              │   (or MCP client call) │           │      │
│              └───────────┬────────────┘           │      │
│                          │ result                 │      │
│                          ▼                        │      │
│              Message Accumulator                  │      │
│              [append tool_call + result]          │      │
│                          │                        │      │
│              Stop? ◄─────┘            stop ◄──────┘      │
│                │                                         │
│                ▼ (continue)                              │
│              LLM (next iteration)                        │
└──────────────────────────────────────────────────────────┘
    │
    ▼ (stop)
Final answer
```

In a multi-agent system, the Action Dispatcher layer routes calls to Subagent Runners, each
of which contains its own Agent Loop. The Subagent Runner is transparent to the orchestrator
— it receives a task string and returns a result string.

---

## 5. Execution Flow

1. Application initializes the message list with system prompt and user task.
2. If MCP: agent sends `tools/list` to MCP server; tool declarations are loaded into the
   tool registry.
3. Agent loop begins. LLM is called with current messages and tool registry.
4. If `finish_reason == "tool_calls"`: dispatcher routes each tool call, results are
   appended to accumulator, loop continues from step 3.
5. If `finish_reason == "stop"`: final response is extracted and returned.
6. If iteration ceiling is reached: loop terminates with a ceiling-reached response.

In multi-agent mode, steps 3–6 run at the orchestrator level. Each subagent invocation in
step 4 triggers its own steps 1–6 in an isolated context with a scoped message list.

---

## 6. Integration Points

| Integration | Direction | Protocol |
|-------------|-----------|----------|
| LLM API (OpenAI, Ollama) | Agent → provider | REST (chat completions) |
| MCP server | Agent → tool provider | Stdio (local) or HTTP+SSE (remote) |
| Subagent | Orchestrator → subagent | In-process function call (subagent runner) |
| External tools (DB, API, FS) | Action dispatcher → service | Service-specific (HTTP, SQL, filesystem) |

---

## 7. Trade-offs and Design Decisions

**Single agent vs. multi-agent:** A single agent with many tools is simpler to deploy but
harder to reason about at scale. Multi-agent systems add coordination overhead and debugging
complexity but enable parallelism and specialization. The practical threshold is roughly six
tools or tasks that require independent parallel execution.

**Inline dispatch vs. MCP:** Inline dispatch (Python functions registered to a dispatcher)
is zero-latency and has no process dependency. MCP adds startup latency, process management
complexity, and a protocol layer. The benefit — reusable, discoverable, language-agnostic
tool definitions — justifies MCP when tools are shared across agents or teams.

**In-memory accumulator vs. checkpointed state:** The message accumulator is held in memory
during the loop. If the agent process restarts mid-loop, the state is lost. For long-running
agents (hours), the accumulator should be checkpointed to durable storage so execution can
resume from the last known state.

**Structured vs. unstructured tool outputs:** Tools that return structured JSON force the
model to parse before reasoning but make outputs predictable and loggable. Tools that return
plain text are easier to implement but produce more LLM overhead. Use structured outputs for
tools called frequently; plain text for tools called rarely with variable results.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| Single-agent loop, action dispatcher, message accumulator | `lab-single-agent-loop` |
| Parallel tool calls, tool result accumulation protocol | `lab-tool-use-loops` |
| Orchestrator, subagent runner, context isolation | `lab-multi-agent` |
| ReAct, plan-and-execute, reflection | `lab-agent-patterns` |
| MCP server, tool discovery, protocol dispatch | `lab-mcp-server` |
| Full system: orchestrator + MCP + patterns | `lab-integration` |

---

## 9. Limitations and Boundaries

**This architecture does not include a persistent agent runtime.** The loop runs for one task
and terminates. Agents that need to run continuously, process events asynchronously, or
maintain state between tasks require runtime infrastructure (task queues, event loops, state
stores) not covered here — those patterns are addressed in `deployment-scaling`.

**Agents in this module are Python-only.** The MCP protocol is language-agnostic but the
lab implementations use the Python `mcp` library. Java-based agent implementations are
covered in `ai-java`.

**The architecture does not cover evaluation, safety guardrails, or observability.** These
concerns are addressed in `evaluation-testing`, `safety-guardrails`, and
`observability-mlops` respectively.

---

## 10. Summary

The agentic system architecture has three composable layers: the single-agent loop (the
execution unit), the multi-agent topology (the coordination layer), and MCP integration (the
tool connectivity layer). The loop is the same at every level — orchestrators and subagents
share the same perception-decide-act structure, differing only in scope and tool set. The
action dispatcher and message accumulator are the two application-owned components that make
the loop work: the dispatcher executes what the model requests; the accumulator ensures the
model sees the complete history of what has already happened.
