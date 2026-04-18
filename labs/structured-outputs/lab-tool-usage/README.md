---
id: "lab-tool-usage"
title: "Tool Usage"
type: "lab-readme"
step: "structured-outputs"
path: "labs/structured-outputs/lab-tool-usage/README.md"
status: "draft"
level: "intermediate"
concepts:
  - "tool-use"
  - "function-calling"
  - "finish-reason"
prerequisites:
  - "docs/structured-outputs/tool-usage.md"
related:
  - "docs/structured-outputs/README.md"
summary: "Implementation lab — demonstrates the full tool call cycle via finish_reason gate, argument extraction, result return, and final response, with side-by-side OpenAI and Anthropic schema differences."
---

# Tool Usage

## Navigation

[Labs](../../README.md) / [Structured Outputs — Labs](../README.md) / Tool Usage

---

## Overview

This lab implements the complete four-phase tool call cycle — declaration, model call, execution, result return — for two single-tool scenarios on the OpenAI-compatible interface, then reproduces the same cycle on the Anthropic API to make schema differences concrete.

**Out of scope:** parallel and sequential tool patterns (covered in `lab-tool-patterns`), schema constraint design (covered in `lab-schema-design`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `tool-use` | All three observations — tools are declared in the request, the model generates a call, the app executes and returns the result |
| `function-calling` | `run_single_tool_cycle()` — `tool_calls[0].function.name` and `tool_calls[0].function.arguments` are the OpenAI fields the app reads to dispatch execution |
| `finish-reason` | `run_single_tool_cycle()` — `finish_reason == "tool_calls"` gates the execution branch; `finish_reason == "stop"` signals the final response |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# ANTHROPIC_API_KEY in .env is optional (observation 3 only)
# Install dependencies (from the module root):
pip install -r labs/structured-outputs/requirements.txt
```

---

## Run

```bash
cd labs/structured-outputs
python lab-tool-usage/main.py
```

---

## Expected Output

```
=== Observation 1: Single tool cycle — get_current_time ===
[1] Sending query with tools...
    finish_reason: tool_calls
    tool called: get_current_time
    arguments: {"timezone": "UTC"}
[2] Executing tool: get_current_time(timezone='UTC')
    result: "2026-04-15 12:34:56 UTC"
[3] Sending result back to model...
    finish_reason: stop
    final response: "The current time in UTC is 12:34:56."

=== Observation 2: Multi-argument tool — convert_currency ===
[1] finish_reason: tool_calls
    tool called: convert_currency
    arguments: {"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"}
[2] result: "85.00 EUR"
[3] final response: "100 USD is approximately 85.00 EUR."

=== Observation 3: Anthropic path — schema differences ===
[Anthropic] stop_reason: tool_use
[Anthropic] content block type: tool_use
[Anthropic] tool name: get_current_time
[Anthropic] input (already a dict): {"timezone": "UTC"}
[Anthropic] result role: user (with tool_result content block)
[Anthropic] final response: "The current time in UTC is 12:34:56."
```

---

## What to observe

- **Finish-reason gate:** in observations 1 and 2, the first response has `finish_reason="tool_calls"` — this is the branch point; if the model answers in text instead, the tool is never executed.
- **Arguments format:** `tool_call.function.arguments` is a JSON string, not a dict — `json.loads` is required before calling the tool function.
- **Anthropic differences:** `stop_reason="tool_use"` instead of `"tool_calls"`; `input` is already a dict; tool result uses `role: "user"` with a `tool_result` content block instead of `role: "tool"`.

---

## Concepts verified

- [ ] `finish_reason == "tool_calls"` gates the tool execution branch — observable at Observation 1 step [1]
- [ ] `tool_call.function.arguments` is a JSON string requiring `json.loads` — observable at Observation 2 arguments line
- [ ] Assistant message must be appended before tool result messages — observable at Failure case
- [ ] Anthropic: `tool_use` block, `input` is already a dict, result uses `role: "user"` — observable at Observation 3

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `run_single_tool_cycle()`, comment out the line `messages.append(msg)` (the assistant message append before the tool result)
- **Expected degradation:**
  - The API returns an error — a `tool` role message without a preceding assistant message violates the protocol
  - Typical error: `"messages must alternate between user and assistant"` or a 400 response
  - The final response is never reached; the function raises before printing step `[3]`

Restore `messages.append(msg)` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves tool use requests via the OpenAI-compatible endpoint |
| Anthropic API | Cloud LLM provider — optional; used in Observation 3 to demonstrate schema differences; skipped if `ANTHROPIC_API_KEY` is absent |
