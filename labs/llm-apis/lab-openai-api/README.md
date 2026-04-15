# lab-openai-api

**Module:** `llm-apis`
**Type:** implementation
**Doc:** `docs/llm-apis/openai-api.md`
**Required:** yes

## What this lab demonstrates

- Chat Completions request structure: `model`, `messages`, `max_tokens`
- Message role semantics: `system`, `user`, `assistant`
- Response parsing: `choices[0].message.content`
- Usage metadata: `prompt_tokens`, `completion_tokens`, `total_tokens`
- `finish_reason` detection and what `"length"` signals
- Multi-turn conversation via explicit message list accumulation

## Prerequisites

- `OPENAI_API_KEY` set in `.env`
- `pip install -r labs/llm-apis/requirements.txt`

## Run

```bash
cd labs/llm-apis
python lab-openai-api/main.py
```

## Expected output

```
=== Observation 1: Basic chat completion ===
Model:         gpt-4o-mini
Response:      <one-sentence answer>
finish_reason: stop
Usage:         prompt=NN  completion=NN  total=NN

=== Observation 2: Forced truncation (finish_reason=length) ===
Response (truncated): <partial response>
finish_reason:        length
WARNING: response was cut off ...

=== Observation 3: Multi-turn conversation ===
Turn 1 — User:      What is temperature in LLM inference?
Turn 1 — Assistant: <answer>
         prompt_tokens so far: NN
Turn 2 ...
Turn 3 ...
```

## Concepts verified

- `finish_reason: "length"` is not an error — it is a signal that requires action
- `prompt_tokens` grows with each turn because full history is resent
- Message list is the caller's responsibility to maintain
