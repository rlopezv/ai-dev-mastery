---
id: "lab-mcp-server"
title: "MCP Server"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/lab-mcp-server/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "Model Context Protocol"
  - "MCP server"
  - "MCP tools"

prerequisites:
  - "docs/ai-agents/mcp.md"
  - "docs/ai-agents/single-agent-loop.md"

related:
  - "docs/ai-agents/architecture.md"
  - "docs/ai-agents/implementation-reference.md"

summary: "Builds an MCP server exposing three tools via the MCP protocol and connects an agent to it via stdio, demonstrating tool discovery, MCP-dispatched tool calls, and equivalence with inline dispatch."
---

## Overview

This lab has two files: `server.py` (the MCP server) and `main.py` (the agent client).
The agent spawns `server.py` as a subprocess via stdio, queries it for available tools
at startup, then runs the same research loop used in `lab-single-agent-loop` — with the
only difference being that tool calls are dispatched via the MCP protocol instead of
in-process function calls.

**Demo 1** (`demo_mcp_agent`) initializes an MCP session, discovers tools via `tools/list`,
and runs the research loop. The log shows tool names at discovery and MCP dispatch at each call.

**Demo 2** (`demo_inline_agent`) runs the identical task with inline dispatch for comparison.
Both demos should produce semantically equivalent final answers.

Out of scope: HTTP+SSE MCP transport, MCP resources, MCP authentication.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `MCP server` | `server.py` — separate process exposing `list_tools` and `call_tool` handlers |
| `MCP tools` | `server.py: list_tools()` — tool discovery endpoint returning 3 tool definitions |
| `Model Context Protocol` | `main.py: run_agent_with_mcp()` — `session.list_tools()` and `session.call_tool()` |
| MCP vs inline equivalence | `main.py: demo_inline_agent()` — same task, same tools, different dispatch path |
| subprocess management | `main.py:103` — `StdioServerParameters(command="python", args=[SERVER_SCRIPT])` |

---

## Setup

```bash
docker-compose --profile light up -d
pip install -r labs/ai-agents/requirements.txt
ollama pull mistral

# Verify MCP server starts cleanly before running main.py
python labs/ai-agents/lab-mcp-server/server.py
# Should hang waiting for input — press Ctrl+C
```

---

## Run

```bash
cd labs/ai-agents/lab-mcp-server
python main.py
```

The agent spawns `server.py` automatically. Do not start `server.py` manually.

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MAX_ITERATIONS` | `10` | Iteration ceiling |

---

## Expected Output

```
============================================================
DEMO 1 — Agent with MCP tool dispatch
Model: mistral  |  Max iterations: 10
============================================================
Task: Search for papers about the Transformer architecture ...
------------------------------------------------------------
MCP session initialized. Discovered 3 tools: ['search_web', 'read_document', 'calculator']
[iteration 1] tool calls: 1
  → tool: search_web  args: {"query": "Transformer architecture"}
  ← result (MCP): Search results:
  1. attention_is_all_you_need — 'Attention Is All You Need': ...
[iteration 2] tool calls: 1
  → tool: read_document  args: {"document_id": "attention_is_all_you_need"}
  ← result (MCP): The Transformer model relies entirely on self-attention ...
[iteration 3] stop — finish_reason=stop, no tool calls
------------------------------------------------------------
FINAL ANSWER (MCP):
The Transformer architecture introduced self-attention ...

============================================================
DEMO 2 — Same task with inline dispatch (comparison)
============================================================
[iteration 1] tool calls: 1
  → tool: search_web  ...
...
------------------------------------------------------------
FINAL ANSWER (inline):
The Transformer architecture introduced self-attention ...
Compare the two answers: same task, same stub tools, same loop ...
```

---

## What to observe

- **Discovery log line**: `MCP session initialized. Discovered 3 tools: [...]` appears once
  at session startup — before the first iteration. The agent did not have this list baked in;
  it queried the server. Compare with Demo 2 where the tool list is hard-coded in `main.py`.

- **`(MCP)` label in result log**: the `← result (MCP):` label distinguishes MCP-dispatched
  results from inline results. The content is identical — the difference is that this result
  traveled over the stdio pipe to the server process and back.

- **Loop structure unchanged**: the `[iteration N]` log format is identical between Demo 1 and
  Demo 2. The agent loop, message accumulation, and stop condition do not change when switching
  from inline to MCP dispatch — only the tool execution path changes.

- **Server process lifecycle**: the server starts when `async with stdio_client(...)` enters
  and is terminated when it exits. The server's stdout does not appear in the agent's log —
  it communicates only via the MCP protocol over the stdio pipe.

---

## Concepts verified

- [ ] `MCP server` — observable as separate process spawned; `server.py` runs independently when tested directly
- [ ] `MCP tools` — observable as `Discovered 3 tools: [...]` log line at session startup
- [ ] `Model Context Protocol` — observable as `← result (MCP):` in tool dispatch log vs `← result:` in inline
- [ ] tool discovery — observable as tool names printed before iteration 1 (not hardcoded in agent)
- [ ] MCP vs inline equivalence — observable as semantically equivalent final answers from both demos

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `demo_mcp_agent()`, modify `SERVER_SCRIPT` to point to a non-existent file path (e.g., `"nonexistent_server.py"`)
- **Expected degradation:**
  - The subprocess fails to start; `stdio_client` raises a transport error during `session.initialize()`
  - The MCP agent cannot run at all
  - Demo 2 (inline) runs successfully immediately after — showing that inline dispatch has no process dependency
  - This demonstrates the process-management cost that MCP adds over inline dispatch

Restore `SERVER_SCRIPT` to the original value after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for the agent loop |
| `server.py` | MCP server subprocess; spawned by `main.py` via stdio |
