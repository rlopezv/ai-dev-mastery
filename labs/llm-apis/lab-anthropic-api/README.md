---
id: "lab-anthropic-api"
title: "Anthropic API"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/lab-anthropic-api/README.md"
status: "draft"
level: "foundational"
concepts:
  - "anthropic-messages-api"
  - "message-role"
  - "finish-reason"
prerequisites:
  - "docs/llm-apis/anthropic-api.md"
related:
  - "docs/llm-apis/README.md"
summary: "Implementation lab — demonstrates Anthropic Messages API schema differences from OpenAI: system as top-level field, content[0].text response path, stop_reason values, and strict message alternation."
---

# Anthropic API

## Navigation

[Labs](../../README.md) / [LLM APIs — Labs](../README.md) / Anthropic API

---

## Overview

This lab sends requests to the Anthropic Messages API and compares its schema to the OpenAI Chat Completions API. It highlights where field paths, field names, and structural rules differ so that the differences become concrete and memorable.

**Out of scope:** streaming (covered in `lab-streaming`), provider abstraction normalization (covered in `lab-api-patterns`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `anthropic-messages-api` | `observe_basic_call()` — `system=` as a top-level field; response text at `content[0].text`; usage via `input_tokens` / `output_tokens` |
| `message-role` | `observe_multi_turn()` — strict `user` / `assistant` alternation enforced server-side; no `system` role in `messages` |
| `finish-reason` | `observe_basic_call()` — `stop_reason: "end_turn"` for normal completion (Anthropic's equivalent of `finish_reason: "stop"`) |

---

## Setup

```bash
# ANTHROPIC_API_KEY must be set in .env
# Install dependencies (from the module root):
pip install -r labs/llm-apis/requirements.txt
```

---

## Run

```bash
cd labs/llm-apis
python lab-anthropic-api/main.py
```

---

## Expected Output

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
Turn 2 — User:      How does it interact with top_p?
Turn 2 — Assistant: <answer>
         input_tokens so far: NNN
Turn 3 — User:      Give a one-line rule of thumb.
Turn 3 — Assistant: <answer>
         input_tokens so far: NNN

=== Observation 3: Schema comparison — Anthropic vs OpenAI ===
Aspect                          OpenAI path                          Anthropic path
System message                  messages[0] role=system              system= (top-level)
Response text                   choices[0].message.content           content[0].text
Stop signal                     finish_reason="stop"                 stop_reason="end_turn"
Input token count               usage.prompt_tokens                  usage.input_tokens
Output token count              usage.completion_tokens              usage.output_tokens
```

---

## What to observe

- **Observation 1:** `stop_reason` is `"end_turn"` not `"stop"`. Code that checks `finish_reason == "stop"` (the OpenAI value) will always evaluate to `False` against Anthropic responses.
- **Observation 2:** `input_tokens` grows each turn as the full history accumulates — same growth pattern as the OpenAI API, despite the different field name.
- **Observation 3:** the schema table makes the provider differences concrete. Notice that `system=` at the top level cannot simply be renamed to fit the OpenAI messages format.

---

## Concepts verified

- [ ] `system=` is a top-level field in Anthropic — not `{"role": "system", ...}` in messages — observable at Observation 3
- [ ] `content[0].text` is the response text path (not `choices[0].message.content`) — observable at Observation 3
- [ ] `stop_reason: "end_turn"` signals normal completion (not `"stop"`) — observable at Observation 1
- [ ] Strict message alternation: sending two consecutive `user` messages raises `400 Bad Request` — observable at Failure case

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_multi_turn()`, after the first `messages.append({"role": "user", ...})`, add a second user message before the API call: `messages.append({"role": "user", "content": "Also, how is it different from top-p?"})`
- **Expected degradation:**
  - Anthropic returns `400 Bad Request` with a message about message role alternation
  - The script raises `anthropic.BadRequestError` — strict alternation is enforced server-side, not just documented

Remove the extra user message append after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Anthropic API | Cloud LLM provider — `ANTHROPIC_API_KEY` required; enforces strict message alternation and uses `stop_reason` instead of `finish_reason` |
