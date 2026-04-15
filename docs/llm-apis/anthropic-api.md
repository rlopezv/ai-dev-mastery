---
id: "llm-apis-anthropic-api"
title: "Anthropic API"
type: "topic"
step: "llm-apis"
path: "docs/llm-apis/anthropic-api.md"
status: "draft"
level: "foundational"

concepts:
  - "anthropic-messages-api"
  - "content-block"
  - "system-prompt"

prerequisites:
  - "docs/llm-apis/openai-api.md"

next:
  - "docs/llm-apis/streaming.md"

related:
  - "docs/llm-apis/ollama-api.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/llm-apis/lab-anthropic-api"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how the Anthropic Messages API differs structurally from the OpenAI Chat Completions API — particularly the separation of the system prompt and the content block response format."
---

## 1. Intuition

The Anthropic Messages API does the same job as the OpenAI Chat Completions API — send a conversation, receive a reply — but with a different schema. The key structural differences are two: the system prompt is a separate top-level field (not a role in messages), and the response content is a list of typed blocks rather than a plain string. Code written for OpenAI does not run against Anthropic without changes.

---

## 2. Explanation

### 2.1 Why

Anthropic designed the Messages API with an explicit separation between the system prompt and the conversation. In the OpenAI API, the system prompt is just the first message with `role: system` — its special status is a convention, not a structural constraint. This means nothing prevents a caller from placing a system message mid-conversation, or from omitting it entirely and using a user message for instructions.

Anthropic's approach makes the separation a schema requirement: `system` is a dedicated top-level string field, and `messages` contains only `user` and `assistant` turns. This forces cleaner separation between developer instructions and conversation content, and allows Anthropic to apply different handling — including caching and safety checks — to the system prompt independently of message history.

The content block response format exists to support multi-modal outputs. When a model can return text, tool calls, and images in a single response, a flat string is insufficient. Anthropic chose a typed list from the start rather than extending a string-based schema later.

### 2.2 How

A request to the Anthropic Messages API (`POST /v1/messages`) contains:

- **`model`**: Claude model identifier (e.g. `claude-opus-4-6`, `claude-haiku-4-5-20251001`)
- **`max_tokens`**: required — unlike OpenAI, this field is not optional
- **`system`**: a string containing developer instructions; not part of `messages`
- **`messages`**: a list of `user` and `assistant` turns only — no `system` role

The response contains:
- **`content`**: a list of content blocks; for text responses, `[{"type": "text", "text": "..."}]`
- **`usage`**: `input_tokens` and `output_tokens` (named differently from OpenAI)
- **`stop_reason`**: `end_turn` (normal), `max_tokens`, or `tool_use`

```python
# See: labs/llm-apis/lab-anthropic-api/main.py
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "What is a context window?"},
    ],
)

reply = response.content[0].text
tokens_used = response.usage.input_tokens + response.usage.output_tokens
```

The text is accessed via `response.content[0].text`, not `response.choices[0].message.content`.

### 2.3 Schema comparison

| Aspect | OpenAI | Anthropic |
|--------|--------|-----------|
| System prompt | `{"role": "system", "content": "..."}` in messages | `system="..."` top-level field |
| Message roles | `system`, `user`, `assistant` | `user`, `assistant` only |
| Response text path | `choices[0].message.content` | `content[0].text` |
| Token usage fields | `usage.prompt_tokens`, `usage.completion_tokens` | `usage.input_tokens`, `usage.output_tokens` |
| `max_tokens` | Optional | Required |
| Stop reason field | `finish_reason` | `stop_reason` |
| Stop reason: normal | `"stop"` | `"end_turn"` |

---

## 3. Table

| Request field | Required | Notes |
|---------------|----------|-------|
| `model` | yes | Use `claude-opus-4-6` for most capable, `claude-haiku-4-5-20251001` for fastest/cheapest |
| `max_tokens` | yes | No default — omitting raises a validation error |
| `system` | no | Recommended for any non-trivial use; separate from messages |
| `messages` | yes | Alternating `user`/`assistant` turns only; must start with `user` |
| `temperature` | no | Same semantics as OpenAI; default is 1.0 |
| `stream` | no | Boolean; activates SSE streaming |

---

## 4. Engineering Implications

The strict alternation requirement in `messages` has a practical consequence: conversation history must start with a `user` message and alternate `user`/`assistant`. Sending two consecutive `user` messages raises a validation error. Applications that accumulate conversation history must enforce alternation, or they will encounter errors that are difficult to debug if the accumulation logic is implicit.

`max_tokens` being required is a useful forcing function. It prevents callers from accidentally leaving the completion length unbounded and incurring unexpected costs. It also means every call has an explicit budget, which aligns with the context window management discipline established in `llm-fundamentals`.

The named difference in token fields (`input_tokens` vs `prompt_tokens`) means that a provider-abstraction layer cannot use the same field accessor for both OpenAI and Anthropic responses. Any code that reads token usage across providers must normalize the response into a common structure.

---

## 5. Implementation Connection

`lab-anthropic-api` exercises the full Anthropic request cycle: constructing the system field, building alternating message history, parsing `content[0].text`, reading `usage.input_tokens` and `usage.output_tokens`, and checking `stop_reason`. It runs the same conversation scenario as `lab-openai-api` to make the structural differences observable side by side.

---

## 6. Failure Modes and Limitations

**Non-alternating messages**: Sending two consecutive `user` messages raises `400 Bad Request` with an error about message ordering. This is the most common mistake when migrating OpenAI-structured conversation history to Anthropic.

**Missing `max_tokens`**: Omitting `max_tokens` raises a validation error immediately. There is no default. New callers who assume the same defaults as OpenAI will see this on their first request.

**Content block index assumption**: `response.content[0].text` assumes the first block is a text block. For pure text responses this is always true, but tool use responses interleave text and `tool_use` blocks. Code that assumes index 0 is always text will fail when tools are introduced in later modules.

---

## 7. Summary

The Anthropic Messages API and the OpenAI Chat Completions API are conceptually equivalent but structurally distinct. Anthropic separates the system prompt from messages as a top-level field, requires `max_tokens`, returns response text inside a content block array, and uses different field names for token usage and stop reasons. These differences mean API-level code is not portable between providers without a normalization layer. Understanding both schemas at this level is prerequisite to building any multi-provider abstraction.
