# lab-tool-patterns

**Module:** `structured-outputs`
**Type:** implementation
**Doc:** `docs/structured-outputs/tool-patterns.md`
**Required:** yes

## What this lab demonstrates

- Pattern 1: single tool — baseline (2 round-trips)
- Pattern 2: parallel tools — weather for two cities in one turn (`len(tool_calls) >= 2`)
- Pattern 3: sequential chain — geocode city then fetch weather using coordinates (3 round-trips)
- Pattern 4: router pattern — model selects the correct tool from three options across four queries

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/structured-outputs/requirements.txt`

## Run

```bash
cd labs/structured-outputs
python lab-tool-patterns/main.py
```

## Expected output

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

## What to observe

- **Parallel:** the first response has `len(msg.tool_calls) >= 2` — both cities are fetched in a single model call, not two sequential calls; round-trips remain 2 regardless of call count
- **Sequential:** `step 2` arguments contain the coordinate values returned by step 1 — trace how `coords_json` flows from the tool result into the next query
- **Router:** expected tool name matches selected tool for all 4 queries — verify the model distinguishes weather, currency, and time intents without explicit routing logic

## Concepts verified

- [ ] Parallel: `len(msg.tool_calls) >= 2` on a single response turn
- [ ] Sequential: step 2 argument contains coordinate values from step 1 output
- [ ] Router: tool name matches expected tool for each query type
- [ ] Round-trip counts: single=2, parallel=2, sequential=3

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `run_parallel_tools()`, change the loop `for i, call in enumerate(msg.tool_calls, 1):` to process only the first call: `for i, call in enumerate(msg.tool_calls[:1], 1):`
- **Expected degradation:**
  - Only one tool result is appended to the messages; the second tool call has no result
  - The final response is incomplete — mentions only one city's weather
  - Some model/API combinations return an error because an expected tool result is missing

Restore the full `msg.tool_calls` slice after the experiment.
