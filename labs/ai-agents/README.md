---
id: "ai-agents-labs-readme"
title: "AI Agents — Labs"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "agent loop"
  - "tool-use loop"
  - "action dispatcher"
  - "orchestrator"
  - "subagent"
  - "ReAct pattern"
  - "Model Context Protocol"

prerequisites:
  - "docs/ai-agents/README.md"
  - "docs/structured-outputs/tool-usage.md"
  - "docs/memory-context/README.md"

next:
  - "labs/frameworks-tools/README.md"

related:
  - "docs/ai-agents/architecture.md"
  - "docs/ai-agents/implementation-reference.md"

implementation_refs:
  - "labs/ai-agents/lab-single-agent-loop"
  - "labs/ai-agents/lab-tool-use-loops"
  - "labs/ai-agents/lab-multi-agent"
  - "labs/ai-agents/lab-agent-patterns"
  - "labs/ai-agents/lab-mcp-server"
  - "labs/ai-agents/lab-integration"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Guides the implementation of agentic systems across six labs covering the single-agent loop, tool-use accumulation, multi-agent coordination, agent patterns, MCP server integration, and full system composition."
---

# AI Agents — Labs

## Navigation

[Labs](../README.md) / AI Agents — Labs

---


## 1. Overview

These labs build an agentic system from its smallest unit to a fully composed application.
Each lab isolates one architectural layer, with the integration lab assembling all layers
into a working end-to-end system.

**What these labs cover:**
- Building a single-agent loop with tool dispatch and stop condition
- Implementing the message accumulation protocol for multi-turn tool interactions
- Coordinating specialized subagents under an orchestrator
- Structuring agent behavior with ReAct, plan-and-execute, and reflection patterns
- Building and connecting to an MCP server for protocol-based tool integration
- Composing all components into a complete agentic application

**What these labs do not cover:**
- Framework-level agent abstractions (LangChain agents, AutoGen — covered in `frameworks-tools`)
- Production agent deployment and persistence (covered in `deployment-scaling`)
- Agent evaluation metrics (covered in `evaluation-testing`)

No corpus is used in this module. Labs use stub tool implementations that simulate external
services (web search, file access, calculator) without requiring live internet access.

---

## 2. Lab Inventory

| Lab | Description | Type | Decision |
|-----|-------------|------|----------|
| `lab-single-agent-loop` | Build a minimal agent loop with tool registry, inline dispatcher, and stop condition | implementation | required |
| `lab-tool-use-loops` | Implement the message accumulation protocol for sequential and parallel tool calls | implementation | required |
| `lab-multi-agent` | Build an orchestrator that delegates sub-tasks to specialized research subagents | integration | required |
| `lab-agent-patterns` | Implement ReAct, plan-and-execute, and reflection on top of the basic loop | implementation | optional |
| `lab-mcp-server` | Build an MCP server with three tools and connect an agent to it via stdio | implementation | required |
| `lab-integration` | Compose orchestrator, subagents, MCP tools, and ReAct into a full agentic application | module-integration | required |

---

## 3. Execution Model

All labs run as Python scripts via `python main.py` from the lab directory. No web server
is started. Labs interact with Ollama directly via the OpenAI-compatible API.

`lab-mcp-server` spawns an MCP server subprocess via stdio — both `main.py` (the agent
client) and `server.py` (the MCP server) must be present in the lab directory.

**Infrastructure required:**

| Lab | Ollama | MCP subprocess |
|-----|--------|----------------|
| `lab-single-agent-loop` | ✅ | — |
| `lab-tool-use-loops` | ✅ | — |
| `lab-multi-agent` | ✅ | — |
| `lab-agent-patterns` | ✅ | — |
| `lab-mcp-server` | ✅ | ✅ (`server.py`) |
| `lab-integration` | ✅ | ✅ (`server.py`) |

**Start Ollama (foundational profile):**

```bash
docker-compose --profile foundational up -d
```

**Install Python dependencies:**

```bash
pip install openai mcp httpx
```

**Run a lab:**

```bash
cd labs/ai-agents/lab-single-agent-loop
python main.py
```

**Run the MCP server lab** (the agent spawns the server automatically via stdio):

```bash
cd labs/ai-agents/lab-mcp-server
python main.py
```

---

## 4. Lab Structure

```text
labs/ai-agents/
├── README.md                        ← this file
├── shared/
│   ├── config.py                    ← Ollama client builder, MODEL, MAX_ITERATIONS
│   ├── dispatcher.py                ← InlineDispatcher, dispatch() with error handling
│   ├── loop.py                      ← run_agent() ceiling-guarded loop
│   └── tools.py                     ← stub tool implementations (search, calculator, file_reader, summarize)
├── lab-single-agent-loop/
│   ├── README.md
│   └── main.py
├── lab-tool-use-loops/
│   ├── README.md
│   └── main.py
├── lab-multi-agent/
│   ├── README.md
│   └── main.py
├── lab-agent-patterns/
│   ├── README.md
│   └── main.py
├── lab-mcp-server/
│   ├── README.md
│   ├── main.py                      ← agent client
│   └── server.py                    ← MCP server process
└── lab-integration/
    ├── README.md
    ├── main.py                      ← orchestrator + agent client
    └── server.py                    ← MCP server for integration lab
```

Labs are isolated: each `main.py` imports only from `shared/` and the standard library.
No lab imports from another lab's directory.

---

## 5. Shared Module

All labs import from `labs/ai-agents/shared/`. The shared module provides:

| Module | Exports | Purpose |
|--------|---------|---------|
| `config.py` | `build_client()`, `MODEL`, `MAX_ITERATIONS` | Ollama OpenAI-compatible client and constants |
| `dispatcher.py` | `InlineDispatcher`, `dispatch()` | Tool name routing, error-safe dispatch, unknown-tool handling |
| `loop.py` | `run_agent()` | Ceiling-guarded agent loop with message accumulation |
| `tools.py` | `search_stub()`, `calculator()`, `file_reader()`, `summarize_stub()` | Stub tool implementations for use in labs |

`run_agent()` is the canonical loop used by all labs. Its signature:

```python
def run_agent(
    client,
    tools: list[dict],
    messages: list[dict],
    dispatcher,
    max_iterations: int = MAX_ITERATIONS,
) -> str:
    ...
```

`lab-mcp-server` replaces `dispatcher` with an MCP client call but uses the same message
accumulation protocol and stop condition.

---

## 6. Mapping to Documentation

| Documentation | Lab | What the lab verifies |
|---------------|-----|-----------------------|
| `docs/ai-agents/single-agent-loop.md` | `lab-single-agent-loop` | Loop terminates on stop condition; ceiling fires on runaway; unknown tool handled as error string |
| `docs/ai-agents/tool-use-loops.md` | `lab-tool-use-loops` | Tool results matched to calls by `tool_call_id`; parallel calls dispatched; history observable per iteration |
| `docs/ai-agents/multi-agent-systems.md` | `lab-multi-agent` | Subagent context is isolated from orchestrator; results summarized before aggregation |
| `docs/ai-agents/agent-patterns.md` | `lab-agent-patterns` | ReAct trace visible in history; reflection ceiling enforced; plan-and-execute re-plans on failure |
| `docs/ai-agents/mcp.md` | `lab-mcp-server` | Tools discovered via `tools/list`; loop identical to inline dispatch version |
| `docs/ai-agents/architecture.md` | `lab-integration` | All architecture layers compose correctly end-to-end |

---

## 7. Validation

**lab-single-agent-loop**
```text
Expected: Each iteration prints: "[Iteration N] Calling tool: <name> with args: <args>"
          and "[Iteration N] Tool result: <result>".
          Final answer printed after "stop" finish_reason.
          Ceiling test task (unanswerable with available tools) terminates with
          "Max iterations reached." after MAX_ITERATIONS loops.
```

**lab-tool-use-loops**
```text
Expected: Parallel tool call turn prints: "Dispatching N tools in parallel: <names>".
          All tool results appended before next LLM call.
          Message history dump at end shows correct role sequence:
          system → user → assistant (tool_calls) → tool (×N) → assistant (stop).
          Per-iteration token count printed.
```

**lab-multi-agent**
```text
Expected: Orchestrator prints "Invoking subagent: research_agent(source=<s>)" for each
          delegated call.
          Subagent prints its own iteration trace independently.
          Orchestrator context size (tokens) printed before and after receiving subagent
          results — difference confirms summarization reduces orchestrator token load.
          Final comparison output produced by orchestrator.
```

**lab-agent-patterns**
```text
ReAct:    Message history contains "Thought:", "Action:", "Observation:" entries.
          Final answer preceded by at least one complete Thought/Action/Observation cycle.

Reflection:
          Prints "Reflection round 1: <issues found>" or "APPROVED".
          Revision ceiling fires if not approved within max_revisions.

Plan-and-execute:
          Prints generated plan (numbered steps) before execution begins.
          Simulated step failure triggers "Re-planning from step N" message.
```

**lab-mcp-server**
```text
Expected: On startup: "MCP session initialized. Discovered 3 tools: search_stub,
          text_summarizer, calculator."
          Agent loop runs and produces correct final answer.
          Running the equivalent task with inline dispatch produces the same answer.
```

**lab-integration**
```text
Expected: Full task completes end-to-end with trace showing:
          - Orchestrator delegating to subagents
          - At least one subagent using MCP-dispatched tools
          - ReAct trace visible in at least one subagent's execution
          - Final answer from orchestrator printed
          Subagent failure simulation: one subagent returns error → orchestrator
          proceeds with partial results and notes the failure in final answer.
```

---

## 8. Common Issues

**Ollama does not return tool calls.** Confirm the model supports tool use. The recommended
model is `mistral` (7B) served via Ollama. If tool calls are not being emitted, verify
`tools=` is passed in the API request and that the system prompt does not suppress tool use.
As a fallback, set `MODEL=gpt-4o-mini` and provide an `OPENAI_API_KEY` environment variable.

**`finish_reason` is `"length"` instead of `"stop"` or `"tool_calls"`.** The model ran out
of output tokens. A tool output was too large and the model could not complete its response.
Increase `max_tokens` in the API call or reduce the stub tool output size in `shared/tools.py`.

**MCP server fails to start.** Verify `mcp` is installed (`pip install mcp`). The server
is spawned as a subprocess via stdio — if `server.py` has a syntax error or a missing import,
the subprocess will exit immediately and the `initialize()` call will fail. Run
`python server.py` directly to diagnose startup errors before running `main.py`.

**`tool_call_id` mismatch error.** The tool result message's `tool_call_id` does not match
the assistant's tool call `id`. This occurs when the tool call is reconstructed from a dict
instead of the response object. Always read `tc.id` directly from the tool call object, not
from a reconstructed dict.

**Subagent prints orchestrator context.** The subagent was initialized with the
orchestrator's full message list. Verify that `run_agent()` for subagents is called with a
fresh `messages` list containing only the subagent's system prompt and delegated task —
not a reference to the orchestrator's accumulator.

---

## 9. Engineering Notes

**Tool call support varies across Ollama model versions.** Mistral 7B supports the
`tools=` parameter in the chat completions API. Smaller models (phi-2, gemma-2b) may not
emit structured tool calls reliably. If tool calls are missing from the response, check the
`tool_calls` field before assuming `finish_reason == "stop"`.

**Stub tools are deterministic.** `shared/tools.py` implements stubs that return
predictable outputs based on input patterns rather than making live network calls. This
makes lab outputs reproducible and the failure case experiments predictable. The trade-off
is that the agent's search results are fixed — they will not reflect any particular real-world
query. This is intentional.

**MCP server restarts are not handled in the labs.** The labs assume the MCP server process
remains alive for the duration of the agent loop. In production, the MCP client must handle
broken pipe errors and attempt server restart. This complexity is out of scope for the labs.

**Message accumulator serialization.** The labs serialize assistant messages to native
Python dicts before appending to the accumulator. This avoids SDK version compatibility
issues when the same list is passed back to the API. Do not append the raw SDK response
object — always convert to a plain dict first.

---

## 10. Next Steps

After completing these labs, proceed to `labs/frameworks-tools/README.md`. The
`frameworks-tools` module shows how LangChain, LlamaIndex, and AutoGen implement agent
abstractions on top of the same loop and dispatch patterns built here.

To understand how agent memory and context interact with the token budget, revisit
`labs/memory-context/lab-context-management/`. The context management strategies from
that lab apply directly to the message accumulator in long-running agent loops.
