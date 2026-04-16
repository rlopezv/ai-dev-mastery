# lab-tool-usage

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

## Concepts verified

- `finish_reason == "tool_calls"` gates the tool execution branch
- `tool_call.function.arguments` is a JSON string requiring `json.loads`
- Assistant message must be appended before tool result messages
- Anthropic: `tool_use` block, `input` is already a dict, result uses `role: "user"` with `tool_result` content
