# lab-context-window

**Module:** llm-fundamentals  
**Type:** observation  
**Doc:** `docs/llm-fundamentals/context-window.md`

---

## What this lab demonstrates

This lab measures token budget consumption before and after sending requests to Ollama. It shows that context window usage is predictable from the tokenizer and that `prompt_eval_count` in the API response confirms the pre-send estimate.

**Observations:**
1. Token cost broken down per prompt component (system, history, user, output)
2. Pre-send estimate vs API-reported `prompt_eval_count`
3. Progressive context fill — how token counts grow as input expands

---

## How to run

```bash
# From the labs/llm-fundamentals/ directory:
python lab-context-window/main.py
```

**Prerequisites:** Ollama running with `llama3.2` loaded. See the module README for setup.

---

## Expected output

```
Model: llama3.2  |  Approximate context limit: 128000 tokens

=== Observation 1: Token cost per component ===
  System prompt:        40 tokens
  Conversation history: 42 tokens
  User message:         23 tokens
  ─────────────────────────────
  Total input:         105 tokens
  Max output:           64 tokens
  Grand total:         169 tokens

=== Observation 2: Estimate vs API token count ===
  Estimated (tiktoken):  10 tokens
  Reported (Ollama):     17 tokens
  Delta:                  7 tokens
  ✓ Estimates agree within 10 tokens (chat template overhead expected)

=== Observation 3: Progressive context fill (limit: 128000) ===
  Step   1 —    16 tokens (  0.0% of 128000-token limit)
  Step   2 —    32 tokens (  0.0% of 128000-token limit)
  Step   3 —    48 tokens (  0.0% of 128000-token limit)
  → Stopping fill at N tokens to stay within MAX_FILL_TOKENS=512
  prompt_eval_count (API): ...
```

---

## What to observe

- **Observation 1:** System prompts cost tokens on every request. A 40-token system prompt × 1,000 daily requests = 40,000 input tokens per day in overhead alone.
- **Observation 2:** The delta between tiktoken estimate and Ollama's `prompt_eval_count` reflects the chat template framing Ollama adds around the prompt. This is normal and expected — budget for it.
- **Observation 3:** Each appended sentence consumes a predictable number of tokens. The `MAX_FILL_TOKENS` cap prevents runaway growth during the observation.

---

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `MODEL` | `llama3.2` | Model to use |
| `NUM_PREDICT` | `64` | Output token budget per request |
| `MAX_FILL_TOKENS` | `512` | Maximum input tokens during progressive fill |
