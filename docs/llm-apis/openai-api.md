---
id: "llm-apis-openai-api"
title: "OpenAI API"
type: "topic"
step: "llm-apis"
path: "docs/llm-apis/openai-api.md"
status: "draft"
level: "foundational"

concepts:
  - "chat-completion-api"
  - "message-role"
  - "usage-metadata"
  - "api-client"

prerequisites:
  - "docs/llm-fundamentals/context-window.md"
  - "docs/llm-fundamentals/inference-parameters.md"

next:
  - "docs/llm-apis/ollama-api.md"

related:
  - "docs/llm-apis/streaming.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/llm-apis/lab-openai-api"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains the OpenAI Chat Completions API contract — message roles, request structure, response parsing, and token usage — which is the de facto standard interface for LLM interaction."
---

# OpenAI API

## Navigation

[Docs](../README.md) / [LLM APIs](README.md) / OpenAI API

---

## 1. Intuition

Calling an LLM is not a function call with a return value — it is an HTTP request that sends a conversation and receives a continuation. The OpenAI Chat Completions API formalizes this as an ordered list of messages, each labeled with a role, sent to a model endpoint that returns the next assistant message. This shape — messages in, message out — is the interface contract that most of the ecosystem has converged on.

---

## 2. Explanation

### 2.1 Why

Before the Chat Completions API, LLMs were typically invoked through a text completion interface: raw text in, raw text out, with no built-in structure for conversation turns or system behavior. This forced every application to manually concatenate system prompts and conversation history into a single string, producing fragile and inconsistent results.

The chat API solves this by making conversation structure explicit. Each message has a declared role (`system`, `user`, `assistant`), so the model can apply role-specific learned behaviors — following instructions from `system`, responding to questions from `user`, maintaining consistency with prior `assistant` turns. The caller does not need to invent a prompt concatenation format; the API contract provides it.

### 2.2 How

A request to the Chat Completions endpoint (`POST /v1/chat/completions`) contains:

- **`model`**: the model identifier (e.g. `gpt-4o`, `gpt-4o-mini`)
- **`messages`**: an ordered list of message objects, each with `role` and `content`
- **Optional parameters**: `temperature`, `max_tokens`, `top_p`, `stream`

The server processes the messages as a single token sequence — system prompt first, then conversation history, then user message — and returns the model's response as a new `assistant` message. The API is stateless: the server retains no memory between requests. The caller is responsible for appending each new exchange to the messages list before the next call.

The response object contains:
- **`choices[0].message`**: the generated assistant message
- **`usage`**: prompt token count, completion token count, and total — used for cost tracking and context budget management
- **`finish_reason`**: `stop` (normal), `length` (hit `max_tokens`), or `content_filter`

```python
# See: labs/llm-apis/lab-openai-api/main.py
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a context window?"},
    ],
    max_tokens=200,
)

reply = response.choices[0].message.content
tokens_used = response.usage.total_tokens
```

### 2.3 Message roles

| Role | Who produces it | What the model does with it |
|------|----------------|----------------------------|
| `system` | Application developer | Establishes model behavior, persona, and constraints |
| `user` | End user or application | The input the model should respond to |
| `assistant` | Model (or injected by application) | Prior responses; used to maintain conversation coherence |

---

## 3. Table

| Request field | Type | Required | Effect |
|---------------|------|----------|--------|
| `model` | string | yes | Selects the model; determines capability and cost |
| `messages` | list | yes | The full conversation context sent to the model |
| `max_tokens` | int | no | Upper bound on completion length; does not guarantee reaching it |
| `temperature` | float | no | Controls output randomness; 0 = deterministic, 2 = very random |
| `top_p` | float | no | Nucleus sampling threshold; alternative to temperature |
| `stream` | bool | no | If true, returns token deltas via SSE instead of a full response |

---

## 4. Engineering Implications

The API is stateless, which means the caller pays the full prompt token cost on every request. In a conversation of 20 turns, the 20th request sends all prior messages in the prompt — token cost grows linearly with conversation length. This is not a performance trade-off; it is the fundamental design of the interface. Context window management (trimming, summarization) must be implemented by the application, not assumed from the server.

The `finish_reason` field must be checked in production code. A `length` finish reason means the response was cut off because `max_tokens` was reached, not because the model finished reasoning. Callers that ignore this silently return incomplete outputs.

---

## 5. Implementation Connection

`lab-openai-api` exercises the full request/response cycle: constructing messages, sending requests, parsing `choices[0].message.content`, reading `usage`, and detecting `finish_reason`. It also demonstrates multi-turn conversation by accumulating messages between calls. Run this lab with a real OpenAI API key.

---

## 6. Failure Modes and Limitations

**Truncated responses without error**: If `max_tokens` is too low, the model stops mid-sentence. There is no exception — only `finish_reason: "length"`. Applications that do not check this field silently return incomplete content.

**Token cost on every turn**: Sending full history on each request means a 10-turn conversation with 200 tokens per turn costs 1,000 prompt tokens on the 10th request, not 200. Naive conversation loops become expensive quickly.

**Rate limits are provider-enforced**: The OpenAI API enforces both requests-per-minute and tokens-per-minute limits. Bursting with parallel requests fails with `429 Too Many Requests`. Retry logic is not optional in production code.

---

## 7. Summary

The OpenAI Chat Completions API defines a conversation as an ordered list of role-labeled messages. The server receives the full history on each request, generates the next assistant message, and returns token usage metadata. The API is stateless: history management, context budgeting, and retry handling are application responsibilities. This interface has become the de facto standard and is implemented by Ollama and many other providers without modification.
