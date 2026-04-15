# lab-api-patterns

**Module:** `llm-apis`
**Type:** implementation
**Doc:** `docs/llm-apis/api-patterns.md`
**Required:** no (optional)

## What this lab demonstrates

- Retry with exponential backoff: injected failures, doubling delay, success on 3rd attempt
- Conversation accumulation: 5-turn exchange with observable token cost growth
- Provider abstraction: `ChatResponse` dataclass, normalized stop reason, identical call site

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `ANTHROPIC_API_KEY` in `.env` (optional — abstraction observation runs Ollama side only if absent)
- `pip install -r labs/llm-apis/requirements.txt`

## Run

```bash
cd labs/llm-apis
python lab-api-patterns/main.py
```

## Expected output

```
=== Observation 1: Retry with exponential backoff ===
  [Attempt 1] Injecting RateLimitError...
  Waiting 1.0s before retry...
  [Attempt 2] Injecting RateLimitError...
  Waiting 2.0s before retry...
  [Attempt 3] Call succeeds.
Final response: <answer>
stop_reason:    stop

=== Observation 2: Conversation accumulation (5 turns) ===
Turn 1  input_tokens=NN   Q: What is a transformer?
        reply: <answer>
Turn 2  input_tokens=NNN  Q: What role does self-attention play in it?
...
Token cost grew from turn 1 to turn 5: compare input_tokens above.

=== Observation 3: Provider abstraction ===
[Ollama]     input=NN  output=NN  stop=stop
Response: <answer>

[Anthropic]  input=NN  output=NN  stop=stop
Response: <answer>

Both responses are ChatResponse instances — caller code is identical.
```

## Concepts verified

- Retry logic doubles delay on each attempt and succeeds after injected failures
- `input_tokens` grows linearly with conversation length — not constant per turn
- `ChatResponse` provides identical structure from both providers
- `stop_reason` is normalized: `"end_turn"` (Anthropic) → `"stop"`, `"max_tokens"` → `"length"`
