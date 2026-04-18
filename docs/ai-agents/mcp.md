---
id: "ai-agents-mcp"
title: "Model Context Protocol"
type: "topic"
step: "ai-agents"
path: "docs/ai-agents/mcp.md"
status: "draft"
level: "intermediate"

concepts:
  - "Model Context Protocol"
  - "MCP server"
  - "MCP tools"

prerequisites:
  - "docs/ai-agents/single-agent-loop.md"
  - "docs/structured-outputs/tool-usage.md"

next:
  - "docs/ai-agents/architecture.md"

related:
  - "docs/ai-agents/agent-patterns.md"
  - "docs/structured-outputs/tool-declaration"

implementation_refs:
  - "labs/ai-agents/lab-mcp-server"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains the Model Context Protocol as an open standard for connecting AI applications to external tools, how MCP servers expose tools to agents, and why MCP is preferable to ad-hoc tool definitions at scale."
---

# Model Context Protocol

## Navigation

[Docs](../README.md) / [AI Agents](README.md) / Model Context Protocol

---

## 1. Intuition

Without MCP, every agent that needs access to a database, an API, or a file system must
implement its own tool definitions and dispatchers. When ten agents need the same database
tool, ten copies of the tool definition exist — each potentially different, each requiring
separate maintenance. MCP defines a standard protocol for this connection: the tool provider
implements it once (the MCP server), and any agent that speaks the protocol gets access
without custom integration code.

---

## 2. Explanation

### 2.1 Why

Ad-hoc tool integration in agents has a scaling problem. Each agent carries its full tool
set as part of its configuration: JSON Schema definitions, Python function implementations,
and dispatcher routing. As the number of agents and tools grows, the maintenance burden
grows with it: updating a tool's parameter schema requires updating every agent that uses
it; adding a new tool requires rebuilding every agent that needs it.

The deeper problem is that tools defined per-agent are not discoverable. An agent cannot
ask "what tools exist?" — it can only use what was baked in at configuration time. This
prevents agents from adapting to new capabilities at runtime.

MCP solves both problems by separating tool definition from agent configuration. The MCP
server owns the tool definitions and exposes them dynamically. The agent queries the server
for available tools at startup and discovers what it can use without any baked-in
configuration. Updating a tool's schema on the server propagates to all connected agents
automatically.

### 2.2 How

MCP defines a message protocol over a transport (standard input/output for local servers,
HTTP+SSE for remote servers). The protocol has three operation types:

**Tool discovery:** The agent sends a `tools/list` request to the MCP server. The server
responds with a list of tool definitions — name, description, and JSON Schema — identical
in structure to the `tools=` parameter of a chat completions API call.

**Tool invocation:** The agent sends a `tools/call` request with the tool name and
arguments. The server executes the tool and returns the result. The result is appended to
the agent's message history as a tool result, exactly as in the standard tool-use loop.

**Resources (optional):** MCP servers can also expose resources — file contents, database
records, API responses — as read-only context injected directly into the agent's context
window, bypassing tool calls entirely.

```text
Agent                    MCP Server
─────                    ──────────
tools/list ────────────► list all tools
           ◄──────────── [tool definitions]
...agent runs loop...
tools/call search(...) ► execute search()
           ◄──────────── result
tools/call lookup(...) ► execute lookup()
           ◄──────────── result
...
```

The agent-facing interface is identical whether tools come from MCP or from a local
dispatcher. The loop structure does not change — only the source of tool definitions and the
execution location change.

### 2.3 Code example

```python
# See: labs/ai-agents/lab-mcp-server/main.py

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_agent_with_mcp(server_script: str, task: str):
    server_params = StdioServerParameters(command="python", args=[server_script])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Discover tools from MCP server
            tools_result = await session.list_tools()
            tools = [mcp_tool_to_openai(t) for t in tools_result.tools]
            # Run agent with discovered tools
            messages = [{"role": "user", "content": task}]
            return await run_agent(client, tools, messages, session)
```

---

## 3. MCP vs. Ad-hoc Tool Integration

| Property | Ad-hoc tool integration | MCP |
|----------|------------------------|-----|
| Tool definition location | Per-agent configuration | MCP server (centralized) |
| Discovery | Static (baked in at build time) | Dynamic (queried at runtime) |
| Schema updates | Requires updating every agent | Updated on server; agents pick up on restart |
| Reuse across agents | Requires copying definitions | Any agent connecting to the server reuses |
| Transport | Direct function calls | Stdio (local) or HTTP+SSE (remote) |
| Ecosystem | Project-specific | Open protocol; server implementations available |

---

## 4. Engineering Implications

**MCP servers run as separate processes.** An MCP server is a process that the agent
communicates with over stdio or HTTP — not an in-process library. This means the server can
be written in any language, deployed independently, and reused across agents in different
runtimes. It also means process management — startup, health checking, restart on failure —
is part of the deployment picture.

**Tool discovery adds startup latency.** Every time an agent initializes an MCP session, it
sends a `tools/list` request. For servers with many tools, this adds a round-trip before the
agent loop starts. In production, tool lists should be cached after the first discovery.

**MCP is not a security boundary.** The MCP server executes whatever tool calls the agent
sends. If the agent is compromised by prompt injection (a user message that causes the agent
to call tools it should not), the MCP server will execute those calls. Authentication and
authorization of tool invocations must be implemented at the server level, not assumed from
the protocol.

**Local MCP servers (stdio) are the starting point.** The `labs/ai-agents/lab-mcp-server`
lab uses stdio transport because it requires no network configuration. Remote MCP servers
use HTTP+SSE and require authentication headers. The agent code is identical for both; only
the `ServerParameters` object changes.

---

## 5. Implementation Connection

`lab-mcp-server` builds an MCP server exposing three tools (web search stub, document
reader, and text summarizer) and an agent that connects to it via stdio. The lab demonstrates
tool discovery at session startup, the full tool-use loop with MCP-dispatched tools, and the
observable difference between baked-in tool dispatch and protocol-based dispatch. The server
implementation uses the `mcp` Python library.

---

## 6. Failure Modes and Limitations

**Protocol version mismatch.** If the MCP client and server use different protocol versions,
the `initialize` handshake may fail silently or return incompatible tool schemas. Both sides
must declare their protocol version explicitly and validate compatibility before entering
the tool loop.

**Server crash during loop.** If the MCP server process crashes while the agent loop is
running, the next `tools/call` request will fail with a transport error. The agent must
detect broken pipe or connection reset errors and attempt server restart or graceful
degradation.

**Tool schema drift.** If the server updates a tool's schema (adding a required parameter)
while agents are connected, those agents will continue sending requests conforming to the
old schema until they restart and re-discover. Long-lived agent processes must handle schema
validation errors from the server and reinitialize when they occur.

---

## 7. Summary

The Model Context Protocol standardizes how agents connect to external tools by defining a
message protocol for tool discovery, invocation, and result return. The agent-facing
behavior is identical to ad-hoc tool use — the same tool-use loop, the same message
accumulation, the same stop condition — but tool definitions come from a running MCP server
rather than being baked into the agent's configuration. This separation enables tool reuse
across agents, dynamic discovery of new capabilities, and centralized schema management.
MCP is the foundation for the tool connectivity layer in multi-agent systems at scale.
