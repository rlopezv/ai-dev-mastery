---
id: "lab-semantic-kernel"
title: "Semantic Kernel — Kernel, Plugins, and Planner"
type: "lab-readme"
step: "frameworks-tools"
path: "labs/frameworks-tools/lab-semantic-kernel/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "Semantic Kernel"
  - "kernel"
  - "plugin"
  - "planner"
  - "native function"
  - "semantic function"

prerequisites:
  - "docs/frameworks-tools/semantic-kernel.md"
  - "docs/structured-outputs/tool-usage.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/frameworks-tools/framework-comparison.md"

summary: "Implements a Semantic Kernel application with native and semantic plugins, demonstrating direct function invocation, planner-based function selection, and explicit chained invocation."
---

# Semantic Kernel — Kernel, Plugins, and Planner

## Navigation

[Labs](../../README.md) / [Frameworks and Tools — Labs](../README.md) / Semantic Kernel — Kernel, Plugins, and Planner

---


## Overview

This lab builds a Semantic Kernel application in three parts:

**Demo 1 — Direct invocation.** Registers a `MathPlugin` (two native functions) and a
`DocumentPlugin` (two semantic functions backed by prompt templates). Invokes each function
directly via `kernel.invoke()` to confirm registration and output.

**Demo 2 — Planner.** Issues a task that requires two sequential plugin functions without
naming them. The planner (`FunctionChoiceBehavior="auto"`) reads all function descriptions
and selects the appropriate functions. The learner observes that description quality drives
selection quality.

**Demo 3 — Explicit chained invocation.** Calls `summarize` and `format_report` in
explicit sequence, passing the output of the first as input to the second. Contrasts with
the planner approach — explicit control, predictable order.

Out of scope: semantic function YAML files, memory stores, C# SK, and SK agent patterns.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `kernel` | `main.py:build_kernel()` — `Kernel()` with `add_service(OpenAIChatCompletion(...))` |
| `plugin` | `main.py` — `kernel.add_plugin(MathPlugin(), plugin_name="Math")` registers all `@kernel_function` methods |
| `native function` | `main.py:MathPlugin` — `multiply` and `square_root` decorated with `@kernel_function` |
| `semantic function` | `main.py:DocumentPlugin` — `summarize` and `format_report` backed by inline prompt templates |
| `planner` | `main.py:demo_planner()` — `OpenAIChatPromptExecutionSettings(function_choice_behavior="auto")` |

---

## Setup

```bash
# Semantic Kernel requires OpenAI API
export OPENAI_API_KEY=sk-...

# Install dependencies
pip install -r labs/frameworks-tools/requirements.txt
```

---

## Run

```bash
cd labs/frameworks-tools/lab-semantic-kernel
python main.py
```

Environment variable overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required — OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model used by the kernel |

> **Note:** `asyncio.run(main())` is used as the entry point. In a Jupyter notebook,
> use `await main()` instead to avoid `RuntimeError: This event loop is already running`.

---

## Expected Output

```
========== DEMO 1 — Direct plugin function invocation ==========

--- Native function: Math.multiply ---
  Result: 42.0 × 17.0 = 714.0

--- Native function: Math.square_root ---
  Result: √714.0 = 26.7208

--- Semantic function: Documents.summarize ---

[Summary]
- **Multi-layer graph**: HNSW constructs a hierarchical graph with long-range
  connections at the top layer and progressively shorter connections below.
- **Greedy traversal**: Queries enter at the top and greedy-walk toward the
  target vector, descending through layers of increasing granularity.
- **Configurable parameters**: M and ef_search control the recall-latency
  trade-off without requiring index rebuilds.

========== DEMO 2 — Planner selects plugin functions ==========
Task: Summarize the following technical text and then format the summary...

Planner execution (verbose):

[Final output]
# Vector Search — Technical Report

Vector search using HNSW enables efficient approximate nearest-neighbor retrieval
through a hierarchical navigable graph structure.

1. **Multi-layer graph**: HNSW constructs layers with long-range connections at
   the top and short-range connections at the bottom.
2. **Greedy traversal**: Queries enter at the top layer and descend toward the target.
3. **Parameter control**: M and ef_search adjust recall and latency trade-offs.

========== DEMO 3 — Explicit chained invocation ==========

--- Step 1: Documents.summarize ---
- **Orchestrator-subagent**: ...
- **Context isolation**: ...
- **Failure propagation**: ...

--- Step 2: Documents.format_report ---

[Final report]
# Multi-Agent Coordination — Technical Report
...
```

---

## What to observe

- **Description drives planner selection in Demo 2**: the `summarize` function is
  selected because its description says "Summarizes the provided technical text into
  exactly three bullet points" — this matches the task's "summarize" intent. The
  `format_report` function is selected next because its description says "formats a
  bullet-point summary" — matching the second step of the task. Remove specificity from
  either description (failure case) and the planner skips that function.

- **Native vs. semantic function output in Demo 1**: `multiply` and `square_root` return
  deterministic string values (no LLM call). `summarize` returns LLM-generated text.
  Both types are invoked identically via `kernel.invoke()` — the kernel abstracts the
  implementation difference.

- **Explicit vs. planner-based execution in Demo 2 vs. Demo 3**: Demo 2 uses one
  `invoke_prompt` call and lets the planner determine the function sequence. Demo 3
  uses two `kernel.invoke()` calls in explicit order. Demo 3 is predictable and easily
  testable. Demo 2 adapts to new task descriptions without code changes.

---

## Concepts verified

- [ ] `kernel` — observable as the central object that holds `Math` and `Documents` plugins and the OpenAI service
- [ ] `plugin` — observable as `kernel.plugins["Math"]` and `kernel.plugins["Documents"]` containing their functions
- [ ] `native function` — observable as deterministic `42.0 × 17.0 = 714.0` output (no LLM variability)
- [ ] `semantic function` — observable as `summarize` producing bullet points via an LLM call
- [ ] `planner` — observable as Demo 2 selecting both `summarize` and `format_report` without naming them

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `DocumentPlugin.summarize`, change the `@kernel_function` description to:
  ```python
  description="Processes text."
  ```
- **Expected degradation:**
  - Demo 2's planner does not select `Documents.summarize` for the summarization step
  - The planner may skip directly to `format_report` (producing a report from unstructured text)
    or answer the task without using any plugin
  - The output lacks the three-bullet structure that `summarize` would have produced
  - This demonstrates that the `description` field is the planner's primary selection signal

Restore the original description after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| OpenAI API | Required — provides the LLM for all kernel invocations; Ollama is not supported by this lab |
