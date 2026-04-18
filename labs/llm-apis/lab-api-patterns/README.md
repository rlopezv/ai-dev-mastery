---
id: "lab-api-patterns"
title: "API Patterns"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/lab-api-patterns/README.md"
status: "draft"
level: "foundational"
concepts:
  - "retry-with-backoff"
  - "provider-abstraction"
  - "conversation-accumulation"
prerequisites:
  - "docs/llm-apis/api-patterns.md"
related:
  - "docs/llm-apis/README.md"
summary: "Implementation lab — demonstrates retry with exponential backoff, conversation token accumulation across turns, and provider abstraction via a normalized ChatResponse dataclass."
---

# API Patterns
## Navigation

[Labs](../../README.md) / [LLM APIs — Labs](../README.md) / API Patterns

---

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

## What to observe

- **Observation 1:** retry delay doubles each attempt (1s → 2s). The third attempt succeeds without any code change — the backoff absorbed the transient failures.
- **Observation 2:** `input_tokens` is not constant — it grows with each turn because the full history is resent. By turn 5 it includes all 5 exchanges.
- **Observation 3:** the call site is identical for Ollama and Anthropic — `run_and_print(name, response)` doesn't know which provider produced the result.

---

## Concepts verified

- [ ] Retry logic doubles delay on each attempt and succeeds after injected failures
- [ ] `input_tokens` grows linearly with conversation length — not constant per turn
- [ ] `ChatResponse` provides identical structure from both providers
- [ ] `stop_reason` is normalized: `"end_turn"` (Anthropic) → `"stop"`, `"max_tokens"` → `"length"`

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_retry_with_backoff()`, change `except RateLimitError:` to `except ValueError:`
- **Expected degradation:**
  - The injected `RateLimitError` is not caught — it propagates immediately on the first attempt
  - No retry occurs; the script raises `openai.RateLimitError` before any backoff
  - Shows that retry logic must explicitly enumerate the error types it handles — a catch-all `except Exception` would mask non-retryable errors

Restore `except RateLimitError:` after the experiment.
