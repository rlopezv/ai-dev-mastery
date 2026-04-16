# Lab: lab-tool-patterns
# Module: structured-outputs
# Doc reference: docs/structured-outputs/tool-patterns.md

import json
import logging
import sys

sys.path.insert(0, ".")
from shared.config import (  # noqa: E402
    MAX_TOKENS,
    OLLAMA_MODEL,
    assert_ollama_ready,
    build_client,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool declarations
# ---------------------------------------------------------------------------
TOOL_GET_WEATHER = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Return current weather for a city by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name."}
            },
            "required": ["city"],
        },
    },
}

TOOL_GET_WEATHER_BY_COORDS = {
    "type": "function",
    "function": {
        "name": "get_weather_by_coords",
        "description": "Return current weather for a latitude/longitude coordinate pair.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude."},
                "lon": {"type": "number", "description": "Longitude."},
            },
            "required": ["lat", "lon"],
        },
    },
}

TOOL_GEOCODE_CITY = {
    "type": "function",
    "function": {
        "name": "geocode_city",
        "description": "Return the latitude and longitude for a city name.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name."}
            },
            "required": ["city"],
        },
    },
}

TOOL_CONVERT_CURRENCY = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert an amount between two currencies.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
}

TOOL_GET_CURRENT_TIME = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Return the current time for a timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string"}
            },
            "required": ["timezone"],
        },
    },
}

# ---------------------------------------------------------------------------
# Stub implementations
# ---------------------------------------------------------------------------
_WEATHER_STUBS = {
    "madrid": "22°C, sunny",
    "paris": "18°C, cloudy",
    "tokyo": "28°C, humid",
    "london": "15°C, overcast",
    "berlin": "17°C, partly cloudy",
    "barcelona": "20°C, partly cloudy",
}

_COORDS = {
    "barcelona": {"lat": 41.38, "lon": 2.17},
    "madrid": {"lat": 40.42, "lon": -3.70},
    "paris": {"lat": 48.85, "lon": 2.35},
}

_RATES = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73, "JPY": 154.0}


def get_weather(city: str) -> str:
    return _WEATHER_STUBS.get(city.lower(), f"20°C, clear (stub for {city})")


def get_weather_by_coords(lat: float, lon: float) -> str:
    return f"20°C, partly cloudy (coords: lat={lat}, lon={lon})"


def geocode_city(city: str) -> str:
    coords = _COORDS.get(city.lower(), {"lat": 0.0, "lon": 0.0})
    return json.dumps(coords)


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    rate_from = _RATES.get(from_currency.upper(), 1.0)
    rate_to = _RATES.get(to_currency.upper(), 1.0)
    result = amount / rate_from * rate_to
    return f"{result:.2f} {to_currency.upper()}"


def get_current_time(timezone: str = "UTC") -> str:
    return f"2026-04-15 14:22:00 {timezone}"


TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_weather_by_coords": get_weather_by_coords,
    "geocode_city": geocode_city,
    "convert_currency": convert_currency,
    "get_current_time": get_current_time,
}


def dispatch(name: str, arguments_json: str) -> str:
    if name not in TOOL_REGISTRY:
        return f"Error: unknown tool '{name}'"
    args = json.loads(arguments_json)
    return str(TOOL_REGISTRY[name](**args))


# ---------------------------------------------------------------------------
# Pattern 1: Single tool
# Concept: single-tool — baseline loop: 2 round-trips
# ---------------------------------------------------------------------------
def run_single_tool(client) -> None:
    print("\n=== Pattern 1: Single tool ===")
    query = "What is the weather in Madrid?"
    messages = [{"role": "user", "content": query}]
    tools = [TOOL_GET_WEATHER]
    round_trips = 0

    response = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, tools=tools, tool_choice="auto",
        max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    msg = response.choices[0].message
    finish = response.choices[0].finish_reason

    if finish not in ("tool_calls", "function_call") or not msg.tool_calls:
        print(f"  No tool call. Response: {msg.content}")
        return

    call = msg.tool_calls[0]
    result = dispatch(call.function.name, call.function.arguments)
    print(f"  Tool called: {call.function.name} | args={call.function.arguments}")
    print(f"  Result: {result!r}")

    messages.append(msg)
    messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    final = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    print(f"  Round-trips: {round_trips}")
    print(f"  Final: {final.choices[0].message.content!r}")


# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In run_parallel_tools(), change the loop to process only the first call:
#   for i, call in enumerate(msg.tool_calls[:1], 1):
# - Observe:
#   * only one tool result is appended — the second tool call has no corresponding result
#   * the final response mentions only one city's weather (incomplete)
#   * some APIs return an error because an expected tool result is missing from the conversation

# ---------------------------------------------------------------------------
# Pattern 2: Parallel tools
# Concept: parallel-tools — multiple tool_calls in one response, 2 round-trips
# ---------------------------------------------------------------------------
def run_parallel_tools(client) -> None:
    print("\n=== Pattern 2: Parallel tools ===")
    query = "What is the weather in Paris and Tokyo right now?"
    messages = [{"role": "user", "content": query}]
    tools = [TOOL_GET_WEATHER]
    round_trips = 0

    response = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, tools=tools, tool_choice="auto",
        max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    msg = response.choices[0].message
    finish = response.choices[0].finish_reason

    if finish not in ("tool_calls", "function_call") or not msg.tool_calls:
        print(f"  No tool call. Response: {msg.content}")
        return

    # Concept: parallel-tools — iterate the full list (may have > 1 call)
    num_calls = len(msg.tool_calls)
    print(f"  Tool calls in first response: {num_calls}")

    messages.append(msg)
    for i, call in enumerate(msg.tool_calls, 1):
        args = json.loads(call.function.arguments)
        result = dispatch(call.function.name, call.function.arguments)
        print(f"  [{i}] {call.function.name} | {args} → {result!r}")
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    final = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    print(f"  Round-trips: {round_trips} (regardless of {num_calls} tool calls)")
    print(f"  Final: {final.choices[0].message.content!r}")


# ---------------------------------------------------------------------------
# Pattern 3: Sequential chain
# Concept: sequential-chain — app drives the pipeline, 3 round-trips
# ---------------------------------------------------------------------------
def run_sequential_chain(client) -> None:
    print("\n=== Pattern 3: Sequential chain ===")
    city = "Barcelona"
    round_trips = 0

    # Step 1: geocode city → coordinates
    messages = [{"role": "user", "content": f"What are the coordinates of {city}?"}]
    tools = [TOOL_GEOCODE_CITY]

    response = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, tools=tools, tool_choice="required",
        max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    msg = response.choices[0].message

    if not msg.tool_calls:
        print("  Step 1: no tool call.")
        return

    call = msg.tool_calls[0]
    coords_json = dispatch(call.function.name, call.function.arguments)
    coords = json.loads(coords_json)
    print(f"  Step 1: {call.function.name} | city={city} → {coords}")

    messages.append(msg)
    messages.append({"role": "tool", "tool_call_id": call.id, "content": coords_json})

    # Step 2: fetch weather using coordinates — output of step 1 feeds step 2
    # Concept: sequential-chain — step 2 argument built from step 1 result
    weather_query = f"What is the weather at lat={coords['lat']}, lon={coords['lon']}?"
    messages.append({"role": "user", "content": weather_query})
    tools2 = [TOOL_GET_WEATHER_BY_COORDS]

    response2 = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, tools=tools2, tool_choice="required",
        max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    msg2 = response2.choices[0].message

    if not msg2.tool_calls:
        print("  Step 2: no tool call.")
        return

    call2 = msg2.tool_calls[0]
    weather_result = dispatch(call2.function.name, call2.function.arguments)
    print(f"  Step 2: {call2.function.name} | {call2.function.arguments} → {weather_result!r}")

    messages.append(msg2)
    messages.append({"role": "tool", "tool_call_id": call2.id, "content": weather_result})

    final = client.chat.completions.create(
        model=OLLAMA_MODEL, messages=messages, max_tokens=MAX_TOKENS,
    )
    round_trips += 1
    print(f"  Round-trips: {round_trips}")
    print(f"  Final: {final.choices[0].message.content!r}")


# ---------------------------------------------------------------------------
# Pattern 4: Router pattern
# Concept: router-pattern — model selects tool based on query; N tools declared
# ---------------------------------------------------------------------------
def run_router_pattern(client) -> None:
    print("\n=== Pattern 4: Router pattern ===")
    all_tools = [TOOL_GET_WEATHER, TOOL_CONVERT_CURRENCY, TOOL_GET_CURRENT_TIME]

    queries = [
        ("What's the weather in Berlin?", "get_weather"),
        ("Convert 50 GBP to JPY.", "convert_currency"),
        ("What time is it in New York?", "get_current_time"),
        ("Weather in London, please.", "get_weather"),
    ]

    for query, expected_tool in queries:
        messages = [{"role": "user", "content": query}]
        response = client.chat.completions.create(
            model=OLLAMA_MODEL, messages=messages, tools=all_tools, tool_choice="auto",
            max_tokens=MAX_TOKENS,
        )
        msg = response.choices[0].message
        finish = response.choices[0].finish_reason

        if finish not in ("tool_calls", "function_call") or not msg.tool_calls:
            selected = "(no tool call)"
            match = "?"
        else:
            selected = msg.tool_calls[0].function.name
            match = "✓" if selected == expected_tool else "✗"

        print(f"  Query: {query!r}")
        print(f"    expected={expected_tool} | selected={selected} | {match}")


if __name__ == "__main__":
    assert_ollama_ready()
    client = build_client()

    run_single_tool(client)
    run_parallel_tools(client)
    run_sequential_chain(client)
    run_router_pattern(client)

    print("\n=== Round-trip summary ===")
    print("  Single:      2 round-trips")
    print("  Parallel:    2 round-trips (N simultaneous calls still = 2 trips)")
    print("  Sequential:  3 round-trips (one per pipeline step + final)")
    print("  Router:      2 round-trips per query (model selects, execute, final)")
