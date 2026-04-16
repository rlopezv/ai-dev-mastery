---
id: "ai-agents-readme"
title: "AI Agents"
type: "step-readme"
step: "ai-agents"
path: "docs/ai-agents/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "agent loop"
  - "tool-use loop"
  - "multi-agent systems"
  - "Model Context Protocol"
  - "agentic application"

prerequisites:
  - "memory-context"

next:
  - "docs/ai-agents/agent-fundamentals.md"

related:
  - "docs/memory-context/README.md"
  - "docs/structured-outputs/tool-usage.md"
  - "docs/frameworks-tools/README.md"

implementation_refs:
  - "labs/ai-agents/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Introduces the agent model for LLM applications — how autonomous loops, tool invocation, multi-agent coordination, and protocol-based tool integration compose into agentic systems."
---

## 1. Overview

A single-turn LLM call answers a question. An agent solves a problem. The difference is the
loop: instead of responding once and returning control to the application, an agent reads an
observation, decides on an action (a tool call or a final answer), executes that action,
observes the result, and repeats — until the task is complete or a stop condition is met.

This module builds the agent model from its minimal form — a single LLM in a loop with one
set of tools — to multi-agent systems where a coordinator delegates sub-tasks to specialized
agents. It also covers the Model Context Protocol (MCP), which standardizes how agents
connect to external tools, and the recurring structural patterns that make agents reliable
in production.

The capability this module unlocks is designing systems where the LLM drives control flow
rather than responding to it.

---

## 2. Scope

**Covered:**
- The agent model: loop structure, perception-decide-act cycle, stop conditions
- The single-agent loop: one LLM, one tool set, one execution cycle
- Tool-use loops: multi-turn message accumulation with tool calls and results
- Multi-agent systems: orchestrators, subagents, and result aggregation
- Agent patterns: ReAct, plan-and-execute, and reflection
- Model Context Protocol: standardized tool connectivity for agents

**Not covered:**
- Framework-level agent abstractions (LangChain, AutoGen — covered in `frameworks-tools`)
- Fine-tuning agents for specific tool use (covered in `llm-fundamentals`)
- Evaluation and testing of agentic systems (covered in `evaluation-testing`)
- Production deployment of agent pipelines (covered in `deployment-scaling`)

---

## 3. Key Concepts

**Agent loop** — the fundamental unit of agentic behavior: perceive an observation (tool
result, user message, or environment state), decide on the next action (tool call or final
response), execute, and repeat. The loop runs until a stop condition is reached.

**Tool-use loop** — the message accumulation protocol that governs multi-turn tool
interactions: the model emits a tool call, the application executes it and appends the
result to the conversation, the model is called again with the updated context, and the
cycle continues until `finish_reason == "stop"`.

**Orchestrator** — in a multi-agent system, the agent responsible for decomposing a task
into sub-tasks, invoking specialized subagents for each sub-task, and aggregating their
results into a coherent response.

**Subagent** — a specialized agent invoked by an orchestrator with a scoped task and its
own tool set, operating independently of the full conversation context.

**ReAct pattern** — a structured prompting and execution pattern where the agent alternates
between a reasoning step ("Thought") and an action step (tool call or final answer),
producing a traceable chain of thought alongside each decision.

**Model Context Protocol (MCP)** — an open protocol for connecting AI applications to
external tools and resources, defining message formats for tool discovery, invocation, and
result return over a standardized interface.

**Agentic application** — an application in which an LLM drives the control flow through
a sequence of tool calls and decisions, rather than executing a single query-response cycle.

---

## 4. Concept Map

```text
                      ┌───────────────────────────┐
                      │      Agentic Application   │
                      └──────────────┬────────────┘
                                     │
               ┌─────────────────────┼──────────────────────┐
               ▼                     ▼                        ▼
   ┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────┐
   │  Single-Agent     │  │  Multi-Agent        │  │  MCP Integration     │
   │  Loop             │  │  System             │  │                      │
   │                   │  │  ┌──────────────┐   │  │  MCP Server          │
   │  Perceive         │  │  │  Orchestrator │   │  │  (tool registry)     │
   │  ──────────       │  │  └──────┬───────┘   │  └──────────────────────┘
   │  Decide           │  │         │            │
   │  ──────────       │  │  ┌──────▼───────┐   │
   │  Act (tool call)  │  │  │  Subagents   │   │
   │  ──────────       │  │  └──────────────┘   │
   │  Stop condition   │  └────────────────────┘
   └───────────────────┘
               │
       ┌───────▼────────────────────────────────────┐
       │             Agent Patterns                  │
       │   ReAct  │  Plan-and-Execute  │  Reflection │
       └─────────────────────────────────────────────┘
```

---

## 5. Learning Flow

```text
agent-fundamentals.md   → What an agent is and why the loop is the minimal unit
single-agent-loop.md    → How a single agent perceives, decides, and acts
tool-use-loops.md       → Message accumulation for multi-turn tool interactions
multi-agent-systems.md  → Orchestrators, subagents, and delegation
agent-patterns.md       → ReAct, plan-and-execute, reflection (optional but recommended)
mcp.md                  → Model Context Protocol and standardized tool connectivity
architecture.md         → How all components compose into an agentic system
implementation-reference.md → Implementation patterns across the labs
validation.md           → Criteria for completing this module
```

Topics 1–3 are sequential and required. `multi-agent-systems.md` builds on the
single-agent loop. `agent-patterns.md` can be read in any order after `tool-use-loops.md`.
`mcp.md` requires familiarity with `single-agent-loop.md` and `tool-usage.md` from
`structured-outputs`.

---

## 6. Documentation Structure

```text
docs/ai-agents/
├── README.md                    ← this file
├── agent-fundamentals.md        ← topic: the agent model and loop structure
├── single-agent-loop.md         ← topic: single LLM perception-decide-act cycle
├── tool-use-loops.md            ← topic: multi-turn tool message accumulation
├── multi-agent-systems.md       ← topic: orchestrators and subagents
├── agent-patterns.md            ← topic: ReAct, plan-and-execute, reflection
├── mcp.md                       ← topic: Model Context Protocol
├── architecture.md              ← system architecture
├── implementation-reference.md  ← implementation patterns
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-single-agent-loop` | implementation | Build a minimal agent loop with tool dispatch and stop condition |
| `lab-tool-use-loops` | implementation | Implement multi-turn message accumulation with tool calls and results |
| `lab-multi-agent` | integration | Build an orchestrator that delegates sub-tasks to specialized subagents |
| `lab-agent-patterns` | implementation | Implement ReAct and reflection patterns on top of the basic loop |
| `lab-mcp-server` | implementation | Build and connect to an MCP server exposing tools to an agent |
| `lab-integration` | module-integration | Assemble all components into a full agentic application |

---

## 8. How to Use This Module

Read topics in order: agent-fundamentals → single-agent-loop → tool-use-loops. These three
establish the foundation — every subsequent topic builds on the loop model.

`multi-agent-systems.md` requires the single-agent loop as a prerequisite. `agent-patterns.md`
is optional but recommended for production work — it covers the structural patterns that make
agent behavior predictable. `mcp.md` can be read any time after `single-agent-loop.md`.

Run each lab immediately after the corresponding topic. The labs share a `shared/` module
with the action dispatcher and tool registry — read the labs README before running
individual labs.

---

## 9. Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `structured-outputs` | Tool declarations and tool-call message format are prerequisites |
| `memory-context` | Agent memory builds on the conversation history model from this module |
| `frameworks-tools` | LangChain and AutoGen provide framework-level agent abstractions over the patterns covered here |
| `evaluation-testing` | Agent evaluation strategies build on the observable behaviors defined in this module |

---

## 10. Next Steps

Begin with `docs/ai-agents/agent-fundamentals.md` to understand why the loop is the
minimal unit of agentic behavior before examining the specific implementation structures.
