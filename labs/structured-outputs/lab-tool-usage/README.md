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

**Module:** `structured-outputs`
**Type:** implementation
**Doc:** `docs/structured-outputs/tool-usage.md`
**Required:** yes

## What this lab demonstrates

- Observation 1: single-tool cycle with `get_current_time` — finish_reason, argument extraction, result return, final response
- Observation 2: single-tool cycle with `convert_currency` — multi-argument tool, `json.loads` on arguments
- Observation 3: Anthropic path for `get_current_time` — `tool_use` content block, `input` as dict, `tool_result` role

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/structured-outputs/requirements.txt`
- Anthropic API key in `.env` (observation 3 only, optional)

## Run

```bash
cd labs/structured-outputs
python lab-tool-usage/main.py
```

## Expected output

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

## What to observe

- **finish_reason gate:** in observations 1 and 2, the first response has `finish_reason="tool_calls"` — this is the branch point; if the model answers in text instead, the tool is never executed
- **arguments format:** `tool_call.function.arguments` is a JSON string, not a dict — `json.loads` is required before calling the tool function
- **Anthropic differences:** `stop_reason="tool_use"` instead of `"tool_calls"`; `input` is already a dict; tool result uses `role: "user"` with a `tool_result` content block instead of `role: "tool"`

## Concepts verified

- [ ] `finish_reason == "tool_calls"` gates the tool execution branch
- [ ] `tool_call.function.arguments` is a JSON string requiring `json.loads`
- [ ] Assistant message must be appended before tool result messages
- [ ] Anthropic: `tool_use` block, `input` is already a dict, result uses `role: "user"` with `tool_result` content

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `run_single_tool_cycle()`, comment out the line `messages.append(msg)` (the assistant message append before the tool result)
- **Expected degradation:**
  - The API returns an error — a `tool` role message without a preceding assistant message violates the protocol
  - Typical error: `"messages must alternate between user and assistant"` or a 400 response
  - The final response is never reached; the function raises before printing step `[3]`

Restore `messages.append(msg)` after the experiment.
