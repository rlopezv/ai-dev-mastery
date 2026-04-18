---
id: "ai-agents-implementation-reference"
title: "AI Agents — Implementation Reference"
type: "implementation-reference"
step: "ai-agents"
path: "docs/ai-agents/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "action dispatcher"
  - "tool registry"
  - "message accumulator"
  - "stop condition"
  - "orchestrator"
  - "MCP server"

prerequisites:
  - "docs/ai-agents/architecture.md"

next:
  - "docs/ai-agents/validation.md"

related:
  - "docs/ai-agents/tool-use-loops.md"
  - "docs/ai-agents/multi-agent-systems.md"
  - "docs/ai-agents/mcp.md"

implementation_refs:
  - "labs/ai-agents/lab-single-agent-loop"
  - "labs/ai-agents/lab-tool-use-loops"
  - "labs/ai-agents/lab-multi-agent"
  - "labs/ai-agents/lab-mcp-server"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Maps architecture components to implementation patterns: tool registry construction, action dispatcher design, message accumulator lifecycle, orchestrator delegation, and MCP client initialization."
---

# AI Agents — Implementation Reference

## Navigation

[Docs](../README.md) / [AI Agents](README.md) / AI Agents — Implementation Reference

---

## 1. Implementation Overview

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

The agent architecture maps to five implementation patterns: tool registration, action
dispatch, message accumulation, multi-agent delegation, and MCP client initialization.
These patterns are the application-owned layer between the LLM API and the agent's tools.
The patterns compose: the message accumulator is shared across single-agent and multi-agent
use; the inline action dispatcher is replaced by an MCP client call in MCP-connected agents.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| `inline-dispatch` | Map tool names to Python functions in a dict; execute on call | Single agent, few tools, no cross-agent reuse |
| `mcp-dispatch` | Query MCP server for tool list; call via `session.call_tool()` | Multi-agent systems; shared tools; tool reuse across agents |
| `accumulate-then-call` | Append assistant + tool results before next LLM call | All tool-use loops |
| `orchestrator-delegate` | Wrap subagent runner as a tool; orchestrator calls it via tool call | Multi-agent systems with specialized agents |
| `ceiling-guarded-loop` | Loop with explicit iteration ceiling; return sentinel on ceiling hit | All agent loops |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| Tool registry | `tools: list[dict]` passed to `chat.completions.create(tools=...)` |
| Action dispatcher | `dispatch(tool_call) → str` function with name-routing dict |
| Message accumulator | `messages: list[dict]` maintained in loop scope |
| Stop condition | `finish_reason == "stop"` check + `if iteration >= max_iterations` |
| Orchestrator | `run_agent()` with subagent runner functions in its dispatcher |
| Subagent runner | `run_agent()` called with a scoped message list and specialized tools |
| MCP client | `ClientSession` from `mcp` library; `list_tools()` + `call_tool()` |
| MCP server | Python script with handlers decorated with `@server.tool()` |

---

## 4. Data Structures and Interfaces

```python
# Orientative — see labs/ai-agents/lab-single-agent-loop/main.py

# Tool declaration (passed to LLM API)
tool_declaration = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for current information on a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

# Inline dispatcher — all tool implementations in one dict
TOOL_MAP: dict[str, Callable] = {
    "search_web": search_web,
    "read_document": read_document,
}

def dispatch(tool_call) -> str:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    fn = TOOL_MAP.get(name)
    if fn is None:
        return f"Error: unknown tool '{name}'"
    return str(fn(**args))

# Message accumulator lifecycle
messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
messages.append({"role": "user", "content": user_task})
# Per iteration — append assistant message first, then tool results:
messages.append(assistant_message_dict)       # role: "assistant"
messages.append(tool_result_message)          # role: "tool", one per call

# MCP tool discovery and format conversion
async def load_mcp_tools(session: ClientSession) -> list[dict]:
    result = await session.list_tools()
    return [mcp_tool_to_openai_format(t) for t in result.tools]
```

---

## 5. Design Decisions

**Dispatcher returns strings, not structured objects.**
The `content` field of a tool result message must be a string. All dispatcher
implementations in this module call `str()` or `json.dumps()` on the result before
returning, regardless of what the tool implementation returns internally. This keeps the
accumulation protocol consistent across tools.

**Dispatcher errors are tool results, not exceptions.**
If a tool call fails — wrong arguments, network error, resource not found — the dispatcher
returns an error string (e.g., `"Error: document not found"`) as the tool result. The LLM
receives the error, can decide to retry with different arguments, report the failure, or
proceed with partial results. Raising exceptions from the dispatcher breaks the loop without
giving the LLM a recovery opportunity.

**Message accumulator holds native dicts, not SDK response objects.**
API response objects from the SDK may not serialize cleanly for subsequent API calls
(version differences, extra fields, non-serializable types). The accumulator stores native
Python dicts built from the response before appending. This makes the accumulator portable
across SDK versions and avoids serialization errors when the same list is passed back to
the API.

**Subagent runners use a fresh message list.**
The subagent is initialized with a new message list containing only its system prompt and
the delegated sub-task. The orchestrator's full conversation history is not passed to the
subagent. This context isolation prevents the subagent from being influenced by unrelated
parts of the orchestrator's session and keeps the subagent's context window bounded to its
task.

**MCP tool declarations are converted to OpenAI format at discovery time.**
The `mcp` library returns tool definitions in MCP schema format, which differs from the
OpenAI `tools=` parameter format. The conversion happens once at session initialization and
the converted declarations are reused across all loop iterations. Reconverting on every call
would add unnecessary overhead.

---

## 6. External Dependencies

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| Ollama (mistral) | LLM runtime for agent loops | `light` |
| OpenAI API | Alternative LLM provider (function calling support) | external |
| `mcp` (Python library) | MCP client and server SDK | included in `requirements.txt` |
| `httpx` | Async HTTP for tool implementations (web search stub) | `light` |

---

## 7. Mapping to Labs

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| Inline dispatcher, message accumulator, stop condition | `lab-single-agent-loop` | LLM-driven loop terminates correctly; ceiling fires on runaway |
| Parallel tool calls, accumulation protocol | `lab-tool-use-loops` | Tool results correctly matched to calls; order preserved |
| Orchestrator + subagent runner | `lab-multi-agent` | Sub-tasks delegated with isolated context; results aggregated |
| MCP tool discovery + dispatch | `lab-mcp-server` | Tools discovered dynamically; loop unchanged from inline version |
| ReAct, plan-and-execute, reflection | `lab-agent-patterns` | Patterns reduce trace opacity and improve output quality |
| Full system composition | `lab-integration` | All components operate together end-to-end |

---

## 8. Trade-offs and Constraints

**Inline dispatch vs. MCP:** Inline dispatch is zero-latency (direct function call) and
requires no process management. MCP adds one network round-trip per tool call (stdio or
HTTP) but enables tool sharing and dynamic discovery. For development and simple agents,
inline dispatch is the right default; switch to MCP when tools are shared across agents or
teams.

**Synchronous vs. async tool execution:** The labs use synchronous tool dispatch for
simplicity. In production, tools that involve I/O (HTTP requests, database queries) should
be executed asynchronously — especially in parallel tool call scenarios where all tools can
be dispatched concurrently. Synchronous parallel dispatch serializes what the LLM requested
in parallel, negating the latency benefit.

**Single message accumulator vs. checkpointed state:** An in-memory accumulator is lost if
the agent process restarts. For long-running agent tasks (minutes to hours), the accumulator
should be persisted to a key-value store after each iteration and restored on restart. This
makes the loop resumable at the cost of per-iteration write latency.

---

## 9. Failure Modes

**`tool_call_id` mismatch.** If the tool result message's `tool_call_id` does not exactly
match the `id` in the tool call, the API returns a validation error. This occurs when the
dispatcher reconstructs the tool call object from a dict instead of reading the `id`
directly from the response object.

**Parallel tool result ordering.** When the model emits multiple tool calls in one turn,
all results must be appended before the next LLM call, with each result's `tool_call_id`
matching its originating call. Some API implementations reject out-of-order or incomplete
result sets.

**MCP session not initialized before tool call.** The MCP `ClientSession` must complete its
`initialize()` handshake before any `list_tools()` or `call_tool()` request. Sending a tool
call without initialization returns a protocol error. The initialization must be awaited
before the agent loop starts.

**Subagent receiving orchestrator context.** If the subagent is accidentally initialized
with the orchestrator's full message list instead of a scoped list, it will treat the
orchestrator's full conversation as its own history — producing responses influenced by
unrelated context and consuming the subagent's context window with data it should not see.

---

## 10. Summary

The five core patterns — inline dispatch, MCP dispatch, accumulate-then-call, orchestrator
delegation, and ceiling-guarded loop — are the reusable building blocks of agent
implementations. They map one-to-one to architecture components and are consistent across
all labs in this module. The critical design constraint is that the dispatcher and
accumulator are owned by the application: the LLM decides what to call; the application
decides how to execute it and how to track what has already happened.
