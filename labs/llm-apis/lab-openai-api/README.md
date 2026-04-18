---
id: "lab-openai-api"
title: "OpenAI API"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/lab-openai-api/README.md"
status: "draft"
level: "foundational"
concepts:
  - "chat-completion-api"
  - "message-role"
  - "finish-reason"
prerequisites:
  - "docs/llm-apis/openai-api.md"
related:
  - "docs/llm-apis/README.md"
summary: "Implementation lab — demonstrates the Chat Completions request structure, usage metadata, finish_reason detection, and multi-turn conversation via message list accumulation."
---

# OpenAI API

## Navigation

[Labs](../../README.md) / [LLM APIs — Labs](../README.md) / OpenAI API

---

## Overview

This lab sends requests to the OpenAI Chat Completions endpoint and inspects the response structure, usage metadata, and finish_reason signal. It then builds a multi-turn conversation by accumulating messages across calls.

**Out of scope:** streaming (covered in `lab-streaming`), provider abstraction (covered in `lab-api-patterns`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `chat-completion-api` | `observe_basic_completion()` — constructs the `model`, `messages`, `max_tokens` request and parses `choices[0].message.content` |
| `message-role` | `observe_multi_turn()` — `system`, `user`, and `assistant` roles are set explicitly on each message |
| `finish-reason` | `observe_truncation()` — `max_tokens=5` forces a `finish_reason="length"` response; detection logic issues a warning |

---

## Setup

```bash
# OPENAI_API_KEY must be set in .env
# Install dependencies (from the module root):
pip install -r labs/llm-apis/requirements.txt
```

---

## Run

```bash
cd labs/llm-apis
python lab-openai-api/main.py
```

---

## Expected Output

```
=== Observation 1: Basic chat completion ===
Model:         gpt-4o-mini
Response:      <one-sentence answer>
finish_reason: stop
Usage:         prompt=NN  completion=NN  total=NN

=== Observation 2: Forced truncation (finish_reason=length) ===
Response (truncated): <partial response>
finish_reason:        length
WARNING: response was cut off — increase max_tokens or handle truncation

=== Observation 3: Multi-turn conversation ===
Turn 1 — User:      What is temperature in LLM inference?
Turn 1 — Assistant: <answer>
         prompt_tokens so far: NN
Turn 2 — User:      How does it interact with top_p?
Turn 2 — Assistant: <answer>
         prompt_tokens so far: NNN
Turn 3 — User:      Give a one-line rule of thumb.
Turn 3 — Assistant: <answer>
         prompt_tokens so far: NNN
```

---

## What to observe

- **Observation 1:** `finish_reason` is `"stop"` for normal completion. Check that `response.choices[0].message.content` is populated and that usage fields are non-zero.
- **Observation 2:** `finish_reason="length"` returns HTTP 200 with a truncated response — not an exception. Code that ignores this field will silently consume incomplete answers.
- **Observation 3:** `prompt_tokens` grows with each turn because the full message list is resent on every call. The cost accumulates — turn 3 pays for turns 1 and 2 as well.

---

## Concepts verified

- [ ] `finish_reason: "length"` is not an error — it is a signal that requires action — observable at Observation 2
- [ ] `prompt_tokens` grows with each turn because full history is resent — observable at Observation 3
- [ ] Message list is the caller's responsibility to maintain — observable at Observation 3

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_multi_turn()`, comment out the line `messages.append({"role": "assistant", "content": reply})`
- **Expected degradation:**
  - The conversation loses coherence — the model has no memory of its previous answers
  - Each turn is answered as a fresh question, regardless of prior exchanges
  - `prompt_tokens` stops growing because the history is no longer accumulating

Restore the `messages.append` line after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| OpenAI API | Cloud LLM provider — `OPENAI_API_KEY` required; provides `finish_reason` and usage metadata per response |
