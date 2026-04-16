---
id: "lab-tool-use-loops"
title: "Tool-Use Loops"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/lab-tool-use-loops/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "tool-use loop"
  - "tool result accumulation"
  - "multi-turn tool use"

prerequisites:
  - "docs/ai-agents/tool-use-loops.md"
  - "docs/ai-agents/single-agent-loop.md"

related:
  - "docs/ai-agents/architecture.md"
  - "docs/ai-agents/implementation-reference.md"

summary: "Implements the message accumulation protocol for sequential and parallel tool calls, making the role sequence, tool_call_id matching, and per-iteration token count directly observable."
---

## Overview

This lab implements an instrumented agent loop that traces the four-rule message
accumulation protocol at each iteration. The learner observes the role sequence
(`system → user → assistant(tool_calls) → tool × N → assistant(stop)`) and
per-iteration token counts as the history grows.

**Demo 1** (`demo_sequential`) runs a sequential two-step task (search → read)
and dumps the full message history after completion, showing each message's role
and content preview.

**Demo 2** (`demo_parallel`) submits a task designed to produce parallel tool calls
in a single turn (calculator + search simultaneously), demonstrating Rule 2 (one result
per call) and Rule 3 (all results before re-call).

Out of scope: multi-agent coordination, agent patterns, MCP.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `tool-use loop` | `main.py: run_agent_instrumented()` — ceiling-guarded loop with per-iteration trace |
| `tool result accumulation` (Rule 1) | `main.py:105` — `messages.append(assistant_entry)` before tool results loop |
| `tool result accumulation` (Rule 2) | `main.py:137` — one `messages.append(tool_result)` per `tc` in `msg.tool_calls` |
| `tool result accumulation` (Rule 3) | `main.py` — the `for tc in msg.tool_calls` loop completes before `continue` |
| `multi-turn tool use` | `main.py: print_message_history()` — role sequence visible across all iterations |

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
cd labs/ai-agents/lab-tool-use-loops
python main.py
```

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MAX_ITERATIONS` | `10` | Iteration ceiling |

---

## Expected Output

```
============================================================
DEMO 1 — Sequential tool use (search → read)
============================================================
Task: Search for papers about RAG ...
------------------------------------------------------------
[iteration 1] tokens: prompt=245  completion=38  total=283
[iteration 1] tool call: search_web
  → search_web  args: {"query": "RAG retrieval-augmented generation"}
  ← result [id=abc12345]: Search results:
  1. rag_paper — 'Retrieval-Augmented Generation ...
[iteration 2] tokens: prompt=340  completion=42  total=382
[iteration 2] tool call: read_document
  → read_document  args: {"document_id": "rag_paper"}
  ← result [id=def67890]: Retrieval-Augmented Generation combines ...
[iteration 3] tokens: prompt=510  completion=58  total=568
[iteration 3] stop — finish_reason=stop, no tool calls
------------------------------------------------------------
FINAL ANSWER: RAG combines a pre-trained language model ...

MESSAGE HISTORY (6 messages):
  [00] system      You are a research assistant ...
  [01] user        Search for papers about RAG ...
  [02] assistant   → tool_calls: ['search_web']
  [03] tool        id=abc12345  content: Search results: ...
  [04] assistant   → tool_calls: ['read_document']
  [05] tool        id=def67890  content: Retrieval-Augmented G...
  ... (final assistant message)

============================================================
DEMO 2 — Parallel tool calls
============================================================
[iteration 1] Dispatching 2 tools in parallel: ['calculator', 'search_web']
  → calculator  args: {"expression": "128 * 256"}
  ← result [id=...]: 32768
  → search_web  args: {"query": "Transformer architecture"}
  ← result [id=...]: Search results: ...
[iteration 2] stop — finish_reason=stop, no tool calls
```

---

## What to observe

- **Token growth per iteration**: the `tokens: prompt=N` line grows with each iteration
  because the history accumulates. After iteration 3, the prompt includes the user message,
  two assistant messages with tool calls, and two tool result messages.

- **Role sequence in message history**: the `MESSAGE HISTORY` dump at the end of Demo 1
  shows the exact ordering: `system → user → assistant(tool_calls) → tool → assistant(tool_calls) → tool → assistant(stop)`.
  Rule 1 is visible here — the assistant message with tool calls always appears before the
  tool result at the same index.

- **Parallel dispatch log line**: in Demo 2, if the model emits two tool calls in one turn,
  the log reads `Dispatching 2 tools in parallel: [...]`. Both results are appended before
  the next LLM call, satisfying Rule 3.

- **`tool_call_id` in history**: the `id=` prefix shown in each tool result log confirms
  that each result carries the `tool_call_id` matching its originating call. Mismatched IDs
  cause API validation errors — this is the mechanism Rule 2 protects.

---

## Concepts verified

- [ ] `tool-use loop` — observable as per-iteration log lines with token counts
- [ ] `tool result accumulation` Rule 1 — observable in message history: assistant before tool at each pair
- [ ] `tool result accumulation` Rule 2 — observable as separate `← result [id=...]` lines per call
- [ ] `tool result accumulation` Rule 3 — observable as all results logged before next `[iteration N]` line
- [ ] `multi-turn tool use` — observable in message history dump showing full role sequence

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `run_agent_instrumented()`, move `messages.append(assistant_entry)` to after the tool results loop (violating Rule 1)
- **Expected degradation:**
  - The API returns a validation error: tool result has no matching assistant tool call in history
  - Or the model sees tool results before the call that generated them, producing inconsistent reasoning
  - The loop fails on the second iteration when the API rejects the malformed history

Restore the original position of `messages.append(assistant_entry)` (before the `for tc` loop) after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for the instrumented agent loop |
