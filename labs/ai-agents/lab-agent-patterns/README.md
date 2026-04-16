---
id: "lab-agent-patterns"
title: "Agent Patterns"
type: "lab-readme"
step: "ai-agents"
path: "labs/ai-agents/lab-agent-patterns/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "ReAct pattern"
  - "plan-and-execute"
  - "reflection"

prerequisites:
  - "docs/ai-agents/agent-patterns.md"
  - "docs/ai-agents/tool-use-loops.md"

related:
  - "docs/ai-agents/architecture.md"
  - "docs/prompt-engineering/chain-of-thought.md"

summary: "Implements ReAct, reflection, and plan-and-execute on top of the basic agent loop, making each pattern's structural difference visible in the message history and log output."
---

## Overview

This lab demonstrates three agent patterns by running research tasks through each one
and comparing the resulting behavior and message history structure.

**Demo 1** (`demo_react`) enforces the Thought → Action → Observation format via the
system prompt. The model's reasoning traces are visible in the assistant message content
before each tool call.

**Demo 2** (`demo_reflection`) generates an initial draft answer, then runs a
reflector-reviser cycle up to `MAX_REVISIONS = 3` times. The learner sees each
round's verdict and the revision ceiling firing if the answer is not approved.

**Demo 3** (`demo_plan_and_execute`) separates planning from execution: the planner
generates a numbered plan without calling any tools, then the executor follows the plan
step by step using the same tools as Demo 1.

Out of scope: multi-agent coordination, MCP dispatch, parallel tool calls.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `ReAct pattern` | `main.py: REACT_SYSTEM` — system prompt enforcing Thought/Action/Observation |
| `ReAct pattern` | `main.py: demo_react()` — loop runs with enriched output format |
| `reflection` | `main.py: reflect_and_revise()` — evaluator loop with revision ceiling |
| `reflection` | `main.py: MAX_REVISIONS = 3` — hard ceiling prevents infinite revision loop |
| `plan-and-execute` | `main.py: plan()` — planning call with no tool access |
| `plan-and-execute` | `main.py: demo_plan_and_execute()` — plan passed to executor as starting context |

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
cd labs/ai-agents/lab-agent-patterns
python main.py
```

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `mistral` | Ollama model name |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MAX_ITERATIONS` | `10` | Iteration ceiling for agent loops |

---

## Expected Output

```
============================================================
DEMO 1 — ReAct pattern (Thought → Action → Observation)
============================================================
Task: Search for papers about the ReAct agent pattern ...
------------------------------------------------------------
[iteration 1] tool calls: 1
  → search_web  args: {"query": "ReAct agent pattern reasoning acting"}
  ← result: Search results: ...
[iteration 2] tool calls: 1
  → read_document  args: {"document_id": "react_paper"}
  ← result: ReAct interleaves reasoning traces ...
[iteration 3] stop — finish_reason=stop, no tool calls
------------------------------------------------------------
FINAL ANSWER: ReAct (Reasoning + Acting) ...
Observe: the model's response content before each tool call should contain 'Thought:' traces.

============================================================
DEMO 2 — Reflection (evaluate → revise → re-evaluate)
============================================================
Task: Explain in exactly two sentences ...
------------------------------------------------------------
Initial draft: ReAct adds reasoning traces ...
------------------------------------------------------------
[reflection round 1] Issues found: - Answer has more than two sentences ...
[reflection round 1] Revised answer: ReAct interleaves Thought steps ...
[reflection round 2] APPROVED
------------------------------------------------------------
FINAL ANSWER (after reflection): ReAct adds explicit reasoning traces ...

============================================================
DEMO 3 — Plan-and-execute (plan first, then execute)
============================================================
Task: Research the Transformer architecture ...
------------------------------------------------------------
PLAN:
1. Search for papers about the Transformer architecture using search_web
2. Read the most relevant document using read_document
3. Extract the key technical contribution and benchmark result
------------------------------------------------------------
[iteration 1] tool calls: 1
  → search_web  args: {"query": "Transformer architecture"}
  ...
------------------------------------------------------------
EXECUTION RESULT: The Transformer architecture ...
Observe: the plan was generated before any tool call ...
```

---

## What to observe

- **ReAct Thought traces**: in Demo 1, the model's `content` field in assistant messages
  (visible in the raw loop logs) should contain `Thought:` prefixes before each tool call.
  These traces are what make the loop debuggable — a failed ReAct agent can be diagnosed by
  reading the Thought sequence in the message history.

- **Reflection rounds and ceiling**: in Demo 2, each `[reflection round N]` line shows
  either `Issues found:` or `APPROVED`. If the reflector never approves within 3 rounds,
  the last line reads `Revision ceiling reached (3). Returning last draft.` — the ceiling
  is the only guarantee of termination.

- **Separation of planning and execution**: in Demo 3, the `PLAN:` block appears before any
  `[iteration N]` line. The planner made zero tool calls — the plan is pure reasoning. Only
  the executor (which received the plan as its starting message) makes tool calls. This is the
  plan-and-execute separation of concerns.

- **Trace differences between patterns**: Demo 1 produces 3 LLM calls (one per iteration);
  Demo 2 produces multiple LLM calls (initial draft + reflector + reviser × N); Demo 3
  produces 1 planning call + N executor calls. The token cost difference is a direct
  consequence of each pattern's structure.

---

## Concepts verified

- [ ] `ReAct pattern` — observable as `Thought:` traces in assistant message content during Demo 1
- [ ] `reflection` — observable as `[reflection round N]` log lines with verdict in Demo 2
- [ ] `reflection` ceiling — observable as `Revision ceiling reached` if reflector does not approve
- [ ] `plan-and-execute` separation — observable as plan printed before any iteration log in Demo 3
- [ ] pattern cost difference — observable as different total LLM call counts across demos

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `demo_react()`, replace `REACT_SYSTEM` with a plain system prompt that does not mention Thought, Action, or Observation
- **Expected degradation:**
  - The model makes tool calls without producing Thought traces in its content
  - The message history shows assistant messages with empty `content` and only `tool_calls`
  - Debugging which tool was called for which reason requires inferring intent from arguments alone
  - This demonstrates why explicit reasoning enforcement is the core value of ReAct

Restore `REACT_SYSTEM` in `demo_react()` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| `ollama` | Serves the local LLM for all three pattern implementations |
