# Lab: lab-tool-usage
# Module: structured-outputs
# Doc reference: docs/structured-outputs/tool-usage.md

import json
import logging
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")
from shared.config import (  # noqa: E402
    ANTHROPIC_MODEL,
    MAX_TOKENS,
    OLLAMA_MODEL,
    assert_ollama_ready,
    build_client,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool declarations (Phase 1 of the tool use cycle)
# Concept: tool-declaration — name, description, and parameter schema
# ---------------------------------------------------------------------------
TOOL_GET_CURRENT_TIME = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Return the current date and time for a given timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name, e.g. 'UTC', 'Europe/Madrid'.",
                }
            },
            "required": ["timezone"],
        },
    },
}

TOOL_CONVERT_CURRENCY = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another using a fixed stub rate.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to convert."},
                "from_currency": {"type": "string", "description": "Source currency code, e.g. USD."},
                "to_currency": {"type": "string", "description": "Target currency code, e.g. EUR."},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
}


# ---------------------------------------------------------------------------
# Tool implementations (Phase 3 of the tool use cycle — application executes)
# Concept: tool-use — application retains execution control
# ---------------------------------------------------------------------------
def get_current_time(timezone: str = "UTC") -> str:  # noqa: ARG001
    """Stub: return a fixed timestamp for reproducibility."""
    return f"2026-04-15 12:34:56 {timezone}"


# Stub exchange rates
_RATES = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 154.0}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Stub: convert using fixed rates."""
    rate_from = _RATES.get(from_currency.upper(), 1.0)
    rate_to = _RATES.get(to_currency.upper(), 1.0)
    converted = amount / rate_from * rate_to
    return f"{converted:.2f} {to_currency.upper()}"


# ---------------------------------------------------------------------------
# Tool registry: name → callable
# Concept: tool-use — registry dispatch keeps the loop logic stable
# ---------------------------------------------------------------------------
TOOL_REGISTRY = {
    "get_current_time": get_current_time,
    "convert_currency": convert_currency,
}


def dispatch(tool_name: str, arguments_json: str) -> str:
    """Execute a registered tool by name. Returns result as a string."""
    if tool_name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{tool_name}'"
    # Concept: function-calling — arguments arrive as a JSON string from OpenAI
    args = json.loads(arguments_json)
    result = TOOL_REGISTRY[tool_name](**args)
    return str(result)


# ---------------------------------------------------------------------------
# Observation 1: Single tool cycle — get_current_time
# Concept: tool-call + tool-result — four-phase cycle with finish-reason gate
# ---------------------------------------------------------------------------
def run_single_tool_cycle(client, tool_def: dict, query: str, label: str) -> None:
    print(f"\n=== {label} ===")
    messages = [{"role": "user", "content": query}]
    tools = [tool_def]

    # Phase 2: model call
    print("[1] Sending query with tools...")
    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=MAX_TOKENS,
    )

    msg = response.choices[0].message
    # Concept: function-calling — finish_reason == "tool_calls" gates the branch
    finish = response.choices[0].finish_reason
    print(f"    finish_reason: {finish}")

    if finish not in ("tool_calls", "function_call") or not msg.tool_calls:
        print("    Model answered in text (no tool call). Response:")
        print(f"    {msg.content}")
        return

    tool_call = msg.tool_calls[0]
    print(f"    tool called: {tool_call.function.name}")
    print(f"    arguments (JSON string): {tool_call.function.arguments}")

    # Phase 3: application executes
    print(f"[2] Executing tool: {tool_call.function.name}({tool_call.function.arguments})")
    result = dispatch(tool_call.function.name, tool_call.function.arguments)
    print(f"    result: {result!r}")

    # Phase 4: result return — append assistant message THEN tool result
    # Concept: tool-result — assistant message must precede the tool result message
    messages.append(msg)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    })

    print("[3] Sending result back to model...")
    final_response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )
    final_finish = final_response.choices[0].finish_reason
    final_text = final_response.choices[0].message.content
    print(f"    finish_reason: {final_finish}")
    print(f"    final response: {final_text!r}")


# ---------------------------------------------------------------------------
# Observation 3: Anthropic path
# Concept: function-calling — Anthropic schema differences vs OpenAI
# ---------------------------------------------------------------------------
def run_anthropic_path() -> None:
    print("\n=== Observation 3: Anthropic path — schema differences ===")

    # Check for API key without importing anthropic at module level
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[skipped] ANTHROPIC_API_KEY not set in .env — observation 3 is optional.")
        print("Set ANTHROPIC_API_KEY to observe Anthropic tool use schema differences.")
        return

    try:
        from shared.config import build_anthropic_client  # noqa: PLC0415
        anthropic_client = build_anthropic_client()
    except SystemExit:
        return

    # Anthropic tool declaration format
    anthropic_tool = {
        "name": "get_current_time",
        "description": "Return the current date and time for a given timezone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "IANA timezone name."}
            },
            "required": ["timezone"],
        },
    }

    response = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": "What time is it in UTC?"}],
        tools=[anthropic_tool],
    )

    # Concept: function-calling — Anthropic uses stop_reason "tool_use" (not "tool_calls")
    print(f"[Anthropic] stop_reason: {response.stop_reason}")

    tool_use_block = next((b for b in response.content if b.type == "tool_use"), None)
    if not tool_use_block:
        print("[Anthropic] No tool_use block in response.")
        return

    print(f"[Anthropic] content block type: {tool_use_block.type}")
    print(f"[Anthropic] tool name: {tool_use_block.name}")
    # Concept: function-calling — Anthropic input is already a dict, not a JSON string
    print(f"[Anthropic] input (already a dict, not JSON string): {tool_use_block.input}")

    result = TOOL_REGISTRY[tool_use_block.name](**tool_use_block.input)

    # Concept: tool-result — Anthropic result uses role "user" with tool_result content block
    result_message = {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": result,
            }
        ],
    }
    print(f"[Anthropic] result role: user (with tool_result content block)")

    final = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "user", "content": "What time is it in UTC?"},
            {"role": "assistant", "content": response.content},
            result_message,
        ],
        tools=[anthropic_tool],
    )
    final_text = next((b.text for b in final.content if hasattr(b, "text")), "")
    print(f"[Anthropic] final response: {final_text!r}")


if __name__ == "__main__":
    assert_ollama_ready()
    client = build_client()

    run_single_tool_cycle(
        client,
        TOOL_GET_CURRENT_TIME,
        "What time is it in UTC right now?",
        "Observation 1: Single tool cycle — get_current_time",
    )

    run_single_tool_cycle(
        client,
        TOOL_CONVERT_CURRENCY,
        "How much is 100 US dollars in euros?",
        "Observation 2: Multi-argument tool — convert_currency",
    )

    run_anthropic_path()

    print("\n=== Key observations ===")
    print("  - finish_reason == 'tool_calls' gates the execution branch")
    print("  - arguments is a JSON string (OpenAI) — requires json.loads")
    print("  - assistant message must be appended BEFORE tool result message")
    print("  - Anthropic: stop_reason='tool_use', input is dict, result role='user'")
