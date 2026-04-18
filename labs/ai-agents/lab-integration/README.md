---
id: "lab-integration"
title: "Integration — Full Agent System"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/lab-integration/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "multi-agent systems"
  - "orchestrator"
  - "subagent"
  - "ReAct pattern"
  - "Model Context Protocol"
  - "agent loop"

prerequisites:
  - "docs/ai-agents/architecture.md"
  - "labs/ai-agents/lab-multi-agent/README.md"
  - "labs/ai-agents/lab-mcp-server/README.md"
  - "labs/ai-agents/lab-agent-patterns/README.md"

related:
  - "docs/ai-agents/implementation-reference.md"

summary: "Composes orchestrator, ReAct subagent, MCP-backed subagent, and failure handling into a single end-to-end agentic system, verifying that all architecture layers work together."
---

# Integration — Full Agent System

## Navigation

[Labs](../../README.md) / [AI Agents — Labs](../README.md) / Integration — Full Agent System

---


## Overview

This is the module integration lab. It assembles all components from the preceding labs
into one working system:

- An **orchestrator** that decomposes a research task and delegates to two subagents
- A **ReAct subagent** that uses inline tool dispatch with Thought/Action/Observation traces
- An **MCP subagent** that discovers and invokes tools via an MCP server subprocess
- A **failure simulation** that shows the orchestrator handling partial results when one
  subagent fails

**Demo 1** runs the full composition end-to-end. The log shows all layers: MCP session
startup, orchestrator delegation, ReAct traces in the first subagent, MCP dispatch in the
second, and final synthesis.

**Demo 2** (`demo_failure_handling`) configures one subagent to return an error string.
The orchestrator receives the error as a tool result and produces a partial answer —
demonstrating that error propagation does not crash the loop.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `orchestrator` | `main.py: run_orchestrator()` — delegates to subagents, synthesizes results |
| `subagent` | `main.py: react_research_agent()` — isolated ReAct loop with inline dispatch |
| `subagent` | `main.py: mcp_research_agent()` — isolated loop with MCP dispatch |
| `ReAct pattern` | `main.py: REACT_SUBAGENT_SYSTEM` — Thought/Action/Observation enforcement |
| `Model Context Protocol` | `main.py: mcp_research_agent()` — `session.list_tools()` + `session.call_tool()` |
| `agent loop` | `main.py: run_agent()` and the inline async loop — both layers use the same pattern |
| error propagation | `main.py: demo_failure_handling()` — error string returned as tool result |

---

## Setup

```bash
docker-compose --profile foundational up -d
pip install -r labs/ai-agents/requirements.txt
ollama pull mistral

# Verify the MCP server starts cleanly
python labs/ai-agents/lab-integration/server.py
# Should hang — press Ctrl+C
```

---

## Run

```bash
cd labs/ai-agents/lab-integration
python main.py
```

The agent spawns `server.py` automatically for Demo 1. Demo 2 uses inline dispatch only.

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MAX_ITERATIONS` | `10` | Iteration ceiling |

---

## Expected Output

```
============================================================
DEMO 1 — Full composition: orchestrator + subagents + MCP + ReAct
============================================================
MCP session initialized.
Orchestrator task: Research two AI topics ...
------------------------------------------------------------
  [subagent:react:transformer] Starting
  [iteration 1] tool calls: 1
    → search_web  args: {"query": "Transformer architecture ..."}
    ...
  [iteration 3] stop — finish_reason=stop, no tool calls
  [subagent:react:transformer] Done — 312 chars summarized to 198 chars

  [subagent:mcp:react-pattern] Starting
  [iteration 1] tool calls: 1
    → search_web  args: {"query": "ReAct pattern reasoning acting"}
    ...
  [subagent:mcp:react-pattern] Done
------------------------------------------------------------
Subagent results received by orchestrator:
  transformer: The Transformer introduced self-attention mechanisms ...
  react-pattern: ReAct interleaves reasoning traces (Thought) ...
------------------------------------------------------------
ORCHESTRATOR FINAL ANSWER:
The Transformer architecture replaced RNNs with self-attention ...
The ReAct pattern extends this by adding explicit reasoning ...

============================================================
DEMO 2 — Subagent failure handling
============================================================
Task: Research both the Transformer architecture and RAG ...
(research_rag subagent is configured to fail)
------------------------------------------------------------
[iteration 1] tool calls: 2
  → research_transformer  args: {"query": "Transformer architecture"}
  ← result: The Transformer model relies entirely on self-attention ...
  → research_rag  args: {"query": "RAG technique"}
  ← result: Error: subagent failed to retrieve results (simulated failure)
[iteration 2] stop — finish_reason=stop, no tool calls
------------------------------------------------------------
ORCHESTRATOR FINAL ANSWER (with partial failure):
The Transformer architecture introduced self-attention ...
Note: the RAG research agent encountered an error and no results are available for that topic.
Observe: the orchestrator received an error string from research_rag and produced a partial answer ...
```

---

## What to observe

- **All layers in one trace**: Demo 1 shows three distinct log prefixes: `[subagent:react:transformer]`
  (ReAct inline), `[subagent:mcp:react-pattern]` (MCP dispatch), and the orchestrator-level
  `[iteration N]` lines. Each layer is independently observable in the log.

- **ReAct trace in first subagent**: the `react_research_agent` subagent uses `REACT_SUBAGENT_SYSTEM`
  which enforces `Thought:` prefixes. Look for `Thought:` in the assistant message content
  logged during the subagent's iterations.

- **MCP dispatch in second subagent**: the `mcp_research_agent` subagent's tool calls route
  through the MCP session. Its tool calls hit `server.py` as a subprocess, not an in-process
  function.

- **Error as valid tool result**: in Demo 2, the `← result:` line for `research_rag` reads
  `Error: subagent failed ...`. This is a string — it flows through the same tool result
  message path as a successful result. The orchestrator receives it, reasons over it, and
  produces a partial answer without crashing.

- **Context isolation between subagents**: neither subagent sees the other's work. The
  transformer subagent finishes before the MCP subagent starts. Each has an independent
  message history containing only its own system prompt and query.

---

## Concepts verified

- [ ] `orchestrator` — observable as orchestrator log showing only subagent tool calls, no direct domain tool calls
- [ ] `subagent` (ReAct) — observable as `[subagent:react:transformer]` trace with `Thought:` entries
- [ ] `subagent` (MCP) — observable as `[subagent:mcp:react-pattern]` trace using MCP session
- [ ] `ReAct pattern` — observable as `Thought:` prefixes in ReAct subagent's message content
- [ ] `Model Context Protocol` — observable as MCP subagent's tool results arriving via `session.call_tool()`
- [ ] error propagation — observable as error string in tool result and partial answer in orchestrator

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `demo_failure_handling()`, change the `dispatcher` to use `failing_subagent` for both `research_transformer` and `research_rag`
- **Expected degradation:**
  - Both subagents return error strings as tool results
  - The orchestrator receives two error strings and produces an answer acknowledging both failures
  - The loop terminates cleanly — two error strings are valid tool results
  - The final answer is partial or entirely absent of substantive content
  - This shows that the loop's error safety extends to the orchestrator level

Restore the original `research_transformer` function in the dispatcher after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for orchestrator and both subagents |
| `server.py` | MCP server subprocess for the MCP subagent; spawned by `main.py` |
