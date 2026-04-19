---
id: "lab-tool-patterns"
title: "Tool Patterns"
type: "lab-readme"
step: "structured-outputs"
path: "labs/structured-outputs/lab-tool-patterns/README.md"
status: "draft"
level: "intermediate"
concepts:
  - "tool-use"
  - "parallel-tools"
  - "sequential-chain"
prerequisites:
  - "docs/structured-outputs/tool-patterns.md"
related:
  - "docs/structured-outputs/README.md"
summary: "Implementation lab — benchmarks single, parallel, sequential, and router tool patterns with round-trip counts and observable argument flow between chained calls."
---

# Tool Patterns

## Navigation

[Labs](../../README.md) / [Structured Outputs — Labs](../README.md) / Tool Patterns

---

## Overview

This lab implements all four tool use patterns — single, parallel, sequential chain, and router — against concrete weather, currency, and geocoding tools. It measures API round-trip counts per pattern and makes the message accumulation differences directly observable.

**Out of scope:** the basic tool call cycle (covered in `lab-tool-usage`), schema constraint design (covered in `lab-schema-design`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `tool-use` | All four patterns — the finish-reason loop from `lab-tool-usage` is the shared execution primitive |
| `parallel-tools` | `run_parallel_tools()` — a single model response contains `len(msg.tool_calls) >= 2`; all results are appended before the next API call |
| `sequential-chain` | `run_sequential_chain()` — application hard-codes the pipeline; step 2 argument is extracted from step 1's tool result; 3 round-trips for 2 steps |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# Install dependencies (from the module root):
pip install -r labs/structured-outputs/requirements.txt
```

---

## Run

```bash
cd labs/structured-outputs
python lab-tool-patterns/main.py
```

---

## Expected Output

```
=== Pattern 1: Single tool ===
Round-trips: 2
Tool called: get_weather | city=Madrid
Final: "The weather in Madrid is 22°C and sunny."

=== Pattern 2: Parallel tools ===
Round-trips: 2
Tool calls in first response: 2
  [1] get_weather | city=Paris
  [2] get_weather | city=Tokyo
Final: "Paris is 18°C and cloudy. Tokyo is 28°C and humid."

=== Pattern 3: Sequential chain ===
Round-trips: 3
Step 1: geocode_city | city=Barcelona → lat=41.38, lon=2.17
Step 2: get_weather_by_coords | lat=41.38, lon=2.17 → 20°C, partly cloudy
Final: "Barcelona is 20°C with partly cloudy skies."

=== Pattern 4: Router pattern ===
Query: "What's the weather in Berlin?"      → get_weather ✓
Query: "Convert 50 GBP to JPY"              → convert_currency ✓
Query: "What time is it in New York?"       → get_current_time ✓
Query: "Weather in London and Paris?"       → get_weather (parallel) ✓
```

---

## What to observe

- **Parallel:** the first response has `len(msg.tool_calls) >= 2` — both cities are fetched in a single model call, not two sequential calls; round-trips remain 2 regardless of call count.
- **Sequential:** step 2 arguments contain the coordinate values returned by step 1 — trace how `coords_json` flows from the tool result into the next query.
- **Router:** expected tool name matches selected tool for all 4 queries — the model distinguishes weather, currency, and time intents without explicit routing logic.

---

## Concepts verified

- [ ] Parallel: `len(msg.tool_calls) >= 2` on a single response turn — observable at Pattern 2 output
- [ ] Sequential: step 2 argument contains coordinate values from step 1 output — observable at Pattern 3 step logs
- [ ] Router: tool name matches expected tool for each query type — observable at Pattern 4 output
- [ ] Round-trip counts: single=2, parallel=2, sequential=3 — observable at each pattern header

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `run_parallel_tools()`, change `for i, call in enumerate(msg.tool_calls, 1):` to process only the first call: `for i, call in enumerate(msg.tool_calls[:1], 1):`
- **Expected degradation:**
  - Only one tool result is appended to the messages; the second tool call has no result
  - The final response mentions only one city's weather
  - Some model/API combinations return an error because an expected `tool_call_id` has no matching result message

Restore the full `msg.tool_calls` slice after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves all four pattern observations via the OpenAI-compatible endpoint |
