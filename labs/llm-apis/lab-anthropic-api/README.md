# lab-anthropic-api

**Module:** `llm-apis`
**Type:** implementation
**Doc:** `docs/llm-apis/anthropic-api.md`
**Required:** yes

## What this lab demonstrates

- `system` as a top-level field, not a message role
- Response text at `content[0].text`
- Usage fields: `input_tokens`, `output_tokens`
- `stop_reason: "end_turn"` for normal completions
- Strict `user`/`assistant` alternation requirement
- Side-by-side schema diff table vs OpenAI

## Prerequisites

- `ANTHROPIC_API_KEY` set in `.env`
- `pip install -r labs/llm-apis/requirements.txt`

## Run

```bash
cd labs/llm-apis
python lab-anthropic-api/main.py
```

## Expected output

```
=== Observation 1: Basic Messages API call ===
Model:       claude-haiku-4-5-20251001
Response:    <one-sentence answer>
stop_reason: end_turn
Usage:       input=NN  output=NN

=== Observation 2: Multi-turn conversation (strict alternation) ===
Turn 1 — User:      What is temperature in LLM inference?
Turn 1 — Assistant: <answer>
         input_tokens so far: NN
...

=== Observation 3: Schema comparison — Anthropic vs OpenAI ===
Aspect                          OpenAI path                          Anthropic path
...
```

## Concepts verified

- `system=` is a top-level field in Anthropic — not `{"role": "system", ...}` in messages
- `content[0].text` is the response text path (not `choices[0].message.content`)
- `stop_reason: "end_turn"` signals normal completion (not `"stop"`)
- Strict message alternation: sending two consecutive `user` messages raises `400 Bad Request`
