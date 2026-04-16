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

## What to observe

- **Observation 1:** `stop_reason` is `"end_turn"` not `"stop"`. Code that checks `finish_reason == "stop"` (the OpenAI value) will always evaluate to `False` against Anthropic responses.
- **Observation 2:** `input_tokens` grows each turn as the full history accumulates — same growth pattern as the OpenAI API, despite the different field name.
- **Observation 3:** the schema table makes the provider differences concrete. Notice that `system=` at the top level cannot simply be renamed to fit the OpenAI messages format.

---

## Concepts verified

- [ ] `system=` is a top-level field in Anthropic — not `{"role": "system", ...}` in messages
- [ ] `content[0].text` is the response text path (not `choices[0].message.content`)
- [ ] `stop_reason: "end_turn"` signals normal completion (not `"stop"`)
- [ ] Strict message alternation: sending two consecutive `user` messages raises `400 Bad Request`

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_multi_turn()`, after the first `messages.append({"role": "user", ...})`, add a second user message before the API call: `messages.append({"role": "user", "content": "Also, how is it different from top-p?"})`
- **Expected degradation:**
  - Anthropic returns `400 Bad Request` with a message about message role alternation
  - The script raises `anthropic.BadRequestError` — strict alternation is enforced server-side, not just documented

Remove the extra user message append after the experiment.
