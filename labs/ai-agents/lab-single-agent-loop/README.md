---
id: "lab-single-agent-loop"
title: "Single Agent Loop"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/lab-single-agent-loop/README.md"
status: "draft"
level: "foundational"

concepts:
  - "agent loop"
  - "stop condition"
  - "tool registry"
  - "action dispatcher"
  - "message accumulator"

prerequisites:
  - "docs/ai-agents/single-agent-loop.md"
  - "docs/ai-agents/agent-fundamentals.md"

related:
  - "docs/ai-agents/architecture.md"
  - "docs/ai-agents/implementation-reference.md"

summary: "Implements a ceiling-guarded agent loop with stub tools to demonstrate perceive-decide-act iteration, stop conditions, and the iteration ceiling."
---

# Single Agent Loop

## Navigation

[Labs](../../README.md) / [AI Agents — Labs](../README.md) / Single Agent Loop

---


## Overview

This lab implements the minimal agent loop: a single LLM connected to two stub tools
(`search_web`, `read_document`) that runs until the model stops requesting tool calls
or the iteration ceiling fires.

**Demo 1** (`demo_research`) runs a research task end-to-end: the agent searches,
reads a document, and writes a summary. The learner observes the full
perceive → decide → act → perceive cycle across multiple iterations.

**Demo 2** (`demo_ceiling`) submits an unanswerable task with a deliberate ceiling of 3.
The agent loops, gets no progress, and the ceiling fires — demonstrating the safety
mechanism that prevents infinite loops.

Out of scope: parallel tool calls, multi-agent coordination, live network access.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `agent loop` | `shared/loop.py: run_agent()` — the `for` loop that drives perceive-decide-act |
| `stop condition` | `loop.py:61` — `if not msg.tool_calls:` terminates when no tool calls are emitted |
| `stop condition` (ceiling) | `loop.py:85` — `return "Max iterations reached."` when loop exhausts |
| `tool registry` | `main.py:30` — `TOOLS` list passed to `tools=` in the API call |
| `action dispatcher` | `shared/dispatcher.py: InlineDispatcher` — maps tool names to Python functions |
| `message accumulator` | `loop.py:56` — `messages.append(assistant_entry)` before tool results |

---

## Setup

```bash
# Start Ollama
docker-compose --profile foundational up -d

# Install dependencies
pip install -r labs/ai-agents/requirements.txt

# Pull the model if not already present
ollama pull mistral
```

---

## Run

```bash
cd labs/ai-agents/lab-single-agent-loop
python main.py
```

Environment variable overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MAX_ITERATIONS` | `10` | Iteration ceiling for Demo 1 |

---

## Expected Output

```
============================================================
DEMO 1 — Normal task completion
Model: mistral  |  Max iterations: 10
============================================================
Task: Search for papers about the Transformer architecture, ...
------------------------------------------------------------
[iteration 1] tool calls: 1
  → tool: search_web  args: {"query": "Transformer architecture"}
  ← result: Search results:
  1. attention_is_all_you_need — 'Attention Is All You Need': ...
  ...
[iteration 2] tool calls: 1
  → tool: read_document  args: {"document_id": "attention_is_all_you_need"}
  ← result: The Transformer model relies entirely on self-attention ...
[iteration 3] stop — finish_reason=stop, no tool calls
------------------------------------------------------------
FINAL ANSWER:
The Transformer architecture ... <2-sentence summary>

============================================================
DEMO 2 — Iteration ceiling
============================================================
Task: Find the exact current market capitalization of every S&P 500 ...
Max iterations: 3  (deliberately low to trigger ceiling)
------------------------------------------------------------
[iteration 1] tool calls: 1
  → tool: search_web  args: {"query": "S&P 500 market capitalization"}
  ← result: Search results: ...
[iteration 2] tool calls: 1
  ...
[iteration 3] tool calls: 1
  ...
Iteration ceiling reached (3). Stopping.
------------------------------------------------------------
Result: Max iterations reached.
Expected: 'Max iterations reached.' — stub tools cannot satisfy this task.
```

---

## What to observe

- **Iteration count in Demo 1**: the agent takes exactly 3 iterations — search, read,
  respond. Watch how the message list grows: user → assistant (tool call) → tool result
  → assistant (tool call) → tool result → assistant (final answer).

- **Stop condition triggering**: in iteration 3 of Demo 1, the log line reads
  `stop — finish_reason=stop, no tool calls`. This is the natural stop condition.
  No tool calls in the response means the model has finished.

- **Ceiling firing in Demo 2**: after iteration 3 the log reads
  `Iteration ceiling reached (3). Stopping.` The model was still requesting tool calls —
  the application cut it off. This is the ceiling stop condition, distinct from the
  natural stop.

- **Stub tool determinism**: the same query always returns the same result.
  Notice that Demo 2's repeated searches return identical content — that is why
  the agent cannot make progress and the ceiling fires.

- **Error-safe dispatch**: if you modify a tool call argument to trigger a TypeError,
  the dispatcher returns an error string rather than crashing the loop.

---

## Concepts verified

- [ ] `agent loop` — observable as 3 log lines `[iteration N]` before the final answer in Demo 1
- [ ] `stop condition` (natural) — observable as `stop — finish_reason=stop, no tool calls` in Demo 1
- [ ] `stop condition` (ceiling) — observable as `Iteration ceiling reached (3). Stopping.` in Demo 2
- [ ] `tool registry` — observable as the model correctly naming `search_web` and `read_document`
- [ ] `action dispatcher` — observable as `→ tool:` and `← result:` log pairs for each tool call
- [ ] `message accumulator` — observable as correct chaining: each tool result immediately follows its call

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `demo_research()`, change `max_iterations=MAX_ITERATIONS` to `max_iterations=1`
- **Expected degradation:**
  - Only one tool call is made (`search_web`) before the ceiling fires
  - The model never calls `read_document` and never writes a summary
  - The final answer is `"Max iterations reached."` instead of a research summary
  - This demonstrates that `MAX_ITERATIONS` must accommodate the full task length,
    not just the first tool call

Restore `max_iterations=MAX_ITERATIONS` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM that drives the agent loop |
