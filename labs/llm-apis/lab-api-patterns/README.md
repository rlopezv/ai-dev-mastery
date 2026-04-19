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

## Overview

This lab implements three reusable patterns that apply regardless of provider: retry with exponential backoff around rate-limit errors, conversation accumulation across multi-turn exchanges, and a provider-abstraction layer that normalizes Ollama and Anthropic responses into a single `ChatResponse` dataclass.

**Out of scope:** streaming patterns (covered in `lab-streaming`), raw provider API details (covered in `lab-openai-api`, `lab-anthropic-api`, `lab-ollama-api`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `retry-with-backoff` | `observe_retry_with_backoff()` — injected `RateLimitError` triggers exponential delay (1s → 2s → success); delay doubles each attempt |
| `conversation-accumulation` | `observe_conversation_accumulation()` — 5-turn exchange where `input_tokens` grows visibly with each turn as the full message history is resent |
| `provider-abstraction` | `observe_provider_abstraction()` — `ChatResponse` dataclass normalizes fields from Ollama and Anthropic; `stop_reason` is mapped to a common vocabulary |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# ANTHROPIC_API_KEY in .env is optional — abstraction observation runs Ollama-only if absent
# Install dependencies (from the module root):
pip install -r labs/llm-apis/requirements.txt
```

---

## Run

```bash
cd labs/llm-apis
python lab-api-patterns/main.py
```

---

## Expected Output

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
        reply: <answer>
...
Token cost grew from turn 1 to turn 5: compare input_tokens above.

=== Observation 3: Provider abstraction ===
[Ollama]     input=NN  output=NN  stop=stop
Response: <answer>

[Anthropic]  input=NN  output=NN  stop=stop
Response: <answer>

Both responses are ChatResponse instances — caller code is identical.
```

---

## What to observe

- **Observation 1:** retry delay doubles each attempt (1s → 2s). The third attempt succeeds without any code change — the backoff absorbed the transient failures.
- **Observation 2:** `input_tokens` is not constant — it grows with each turn because the full history is resent. By turn 5 it includes all 5 exchanges.
- **Observation 3:** the call site is identical for Ollama and Anthropic — `run_and_print(name, response)` doesn't know which provider produced the result.

---

## Concepts verified

- [ ] Retry logic doubles delay on each attempt and succeeds after injected failures — observable at Observation 1
- [ ] `input_tokens` grows linearly with conversation length — not constant per turn — observable at Observation 2
- [ ] `ChatResponse` provides identical structure from both providers — observable at Observation 3
- [ ] `stop_reason` is normalized: `"end_turn"` (Anthropic) → `"stop"`, `"max_tokens"` → `"length"` — observable at Observation 3

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_retry_with_backoff()`, change `except RateLimitError:` to `except ValueError:`
- **Expected degradation:**
  - The injected `RateLimitError` is not caught — it propagates immediately on the first attempt
  - No retry occurs; the script raises `openai.RateLimitError` before any backoff
  - Shows that retry logic must explicitly enumerate the error types it handles — a catch-all `except Exception` would mask non-retryable errors

Restore `except RateLimitError:` after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — used in the retry and provider abstraction observations |
| Anthropic API | Cloud LLM provider — optional; used in provider abstraction; skipped if `ANTHROPIC_API_KEY` is absent |
