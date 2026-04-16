---
id: "lab-multi-agent"
title: "Multi-Agent Systems"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/lab-multi-agent/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "multi-agent systems"
  - "orchestrator"
  - "subagent"

prerequisites:
  - "docs/ai-agents/multi-agent-systems.md"
  - "docs/ai-agents/tool-use-loops.md"

related:
  - "docs/ai-agents/architecture.md"
  - "docs/ai-agents/implementation-reference.md"

summary: "Builds an orchestrator that delegates research sub-tasks to specialized subagents, demonstrating context isolation, result summarization, and subagent invocation as tool calls."
---

## Overview

This lab implements a two-level agent system: an orchestrator that decomposes a research
task into sub-tasks and delegates each to a specialized research subagent. Each subagent
runs its own independent agent loop and returns a summarized result to the orchestrator.

**Demo 1** (`demo_orchestration`) runs the full two-level system: the orchestrator
receives a comparison task, invokes two research subagents as tool calls, and synthesizes
their summarized results into a final answer.

**Demo 2** (`demo_context_isolation`) runs one subagent directly to show that its
internal context contains only its own sub-task — no orchestrator history leaks in.

Out of scope: MCP tool dispatch, agent patterns, parallel subagent execution.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `orchestrator` | `main.py: build_orchestrator_tools()` — tool set contains only subagent invocations |
| `subagent` | `main.py: make_research_agent()` — isolated agent with its own loop and tools |
| `multi-agent systems` | `main.py: demo_orchestration()` — outer loop delegates via tool calls to inner loops |
| context isolation | `main.py:72` — `messages = [system_prompt, subtask]` — fresh list, no orchestrator history |
| result summarization | `main.py:83` — `summarize_stub(result, max_sentences=3)` before returning to orchestrator |

---

## Setup

```bash
docker-compose --profile light up -d
pip install -r labs/ai-agents/requirements.txt
ollama pull mistral
```

---

## Run

```bash
cd labs/ai-agents/lab-multi-agent
python main.py
```

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MAX_ITERATIONS` | `10` | Iteration ceiling for orchestrator and subagents |

---

## Expected Output

```
============================================================
DEMO 1 — Orchestrator + subagents
Model: mistral  |  Max iterations: 10
============================================================
Task: Research the Transformer architecture and the RAG technique ...
------------------------------------------------------------
[iteration 1] tool calls: 2
  → research_transformer_agent  args: {"query": "Transformer architecture ..."}
  [subagent:transformer] Starting — query: Transformer architecture ...
  [iteration 1] tool calls: 1
    → search_web  args: {"query": "Transformer architecture"}
    ← result: Search results: ...
  [iteration 2] tool calls: 1
    → read_document  args: {"document_id": "attention_is_all_you_need"}
    ← result: The Transformer model relies ...
  [iteration 3] stop — finish_reason=stop, no tool calls
  [subagent:transformer] Done — result length: 312 chars
  → research_rag_agent  args: {"query": "RAG technique ..."}
  [subagent:rag] Starting — query: RAG technique ...
  ...
  [subagent:rag] Done — result length: 280 chars
  ← result (orchestrator): The Transformer model ...
[iteration 2] stop — finish_reason=stop, no tool calls
------------------------------------------------------------
ORCHESTRATOR FINAL ANSWER:
The Transformer introduced self-attention ... RAG combines retrieval ...

============================================================
DEMO 2 — Context isolation
============================================================
Running research_agent(topic=agent) directly with isolated context.
[subagent:agent] Starting — query: What is the ReAct pattern ...
[iteration 1] tool calls: 1
  → search_web  args: {"query": "ReAct agent pattern"}
  ...
[subagent:agent] Done — result length: 245 chars
------------------------------------------------------------
Subagent result: ReAct interleaves reasoning traces ...
Observe: the subagent's log shows only its own iterations ...
```

---

## What to observe

- **Nested iteration traces**: the subagent's `[iteration N]` lines appear indented inside
  the orchestrator's tool call. The subagent runs its own complete loop — the orchestrator
  is paused at the tool call boundary while the subagent executes.

- **Context isolation**: the `[subagent:X] Starting` log line appears after the orchestrator
  emits the tool call. The subagent has no knowledge of the orchestrator's task or of the
  other subagent's work — it sees only its own system prompt and query.

- **Summarization before return**: the subagent logs `result length: N chars` before
  `summarize_stub` reduces it. The orchestrator never receives the full raw output — only the
  summary. This bounds the orchestrator's context growth.

- **Orchestrator tool set**: the orchestrator only calls `research_transformer_agent` and
  `research_rag_agent` — it never calls `search_web` or `read_document` directly. Domain
  tool calls stay inside the subagents.

---

## Concepts verified

- [ ] `orchestrator` — observable as orchestrator calling only subagent tools, never domain tools directly
- [ ] `subagent` — observable as nested `[subagent:X]` iteration traces per delegated call
- [ ] `multi-agent systems` — observable as two complete independent loops nested inside one outer loop
- [ ] context isolation — observable as subagent log showing only its own sub-task context
- [ ] result summarization — observable as `result length: N chars` reduced before return

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `make_research_agent()`, replace the fresh `messages` list with a copy of a pre-populated orchestrator history list (add `orchestrator_context` as a parameter and pass it in)
- **Expected degradation:**
  - The subagent reasons about the orchestrator's full task instead of just its sub-task
  - Subagent responses reference topics from the orchestrator context that are irrelevant to the delegated query
  - The subagent's `tool_call_id` references may become misaligned if it re-interprets prior messages

Restore the fresh `messages = [system_prompt, subtask]` initialization after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for both orchestrator and subagent loops |
