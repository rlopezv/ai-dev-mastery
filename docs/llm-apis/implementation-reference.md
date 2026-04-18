---
id: "llm-apis-implementation-reference"
title: "LLM APIs — Implementation Reference"
type: "implementation-reference"
step: "llm-apis"
path: "docs/llm-apis/implementation-reference.md"
status: "draft"
level: "foundational"

concepts:
  - "chat-completion-api"
  - "provider-abstraction"
  - "conversation-accumulation"
  - "retry-with-backoff"
  - "streaming"

prerequisites:
  - "docs/llm-apis/architecture.md"

next:
  - "docs/llm-apis/validation.md"

related:
  - "docs/llm-apis/openai-api.md"
  - "docs/llm-apis/anthropic-api.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/llm-apis/lab-openai-api"
  - "labs/llm-apis/lab-ollama-api"
  - "labs/llm-apis/lab-anthropic-api"
  - "labs/llm-apis/lab-streaming"
  - "labs/llm-apis/lab-api-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how the architecture components for LLM API clients map to concrete implementation patterns — SDK usage, schema normalization, conversation management, and retry handling."
---

# LLM APIs — Implementation Reference

## Navigation

[Docs](../README.md) / [LLM APIs](README.md) / LLM APIs — Implementation Reference

---

## 1. Implementation Overview

The architecture for this module has five components: provider SDK, abstraction layer, conversation manager, retry handler, and LLM provider. In code, the provider SDK is a direct dependency (`openai`, `anthropic`), while the abstraction layer, conversation manager, and retry handler are application-owned patterns — not imported libraries. Each lab implements a subset of these patterns, progressing from raw SDK usage to a fully composed client.

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| Direct SDK call | Call provider SDK with no wrapper | Single-purpose scripts; individual lab exercises |
| Abstraction wrapper | Normalize provider schemas into a common response | Any code that may switch providers or run against Ollama locally |
| Conversation accumulator | Append each exchange to a growing message list | Multi-turn applications |
| Retry with backoff | Catch `RateLimitError`/`5xx` and retry with delay | All production API calls |
| Streaming assembler | Iterate chunk deltas and accumulate full text | UI applications; first-token latency sensitive paths |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| Provider SDK — OpenAI/Ollama | `openai.OpenAI` client with optional `base_url` override |
| Provider SDK — Anthropic | `anthropic.Anthropic` client |
| Abstraction layer | `ChatResponse` dataclass + provider-specific factory functions |
| Conversation manager | `list[dict]` with `append` on each exchange |
| Retry handler | `try/except` loop with `time.sleep(delay); delay *= 2` |
| Streaming assembler | `for chunk in stream:` loop with string accumulation |

---

## 4. Data Structures and Interfaces

**Normalized response** — common return type across providers:

```python
# Orientative — see labs/llm-apis/lab-api-patterns/main.py for full implementation
from dataclasses import dataclass

@dataclass
class ChatResponse:
    text: str
    input_tokens: int
    output_tokens: int
    stop_reason: str          # "stop" | "end_turn" | "length" | "max_tokens"
```

**Message format** — OpenAI/Ollama schema (used for both providers via compatible interface):

```python
# Orientative — see labs/llm-apis/lab-openai-api/main.py
Message = dict  # {"role": "system"|"user"|"assistant", "content": str}
Messages = list[Message]
```

**Provider factory functions**:

```python
# Orientative — see labs/llm-apis/lab-api-patterns/main.py
def call_openai(client, model: str, messages: Messages) -> ChatResponse: ...
def call_anthropic(client, model: str, system: str, messages: Messages) -> ChatResponse: ...
```

The Anthropic factory requires `system` as a separate argument because it is a top-level field in the Anthropic API, not part of `messages`.

---

## 5. Design Decisions

**`ChatResponse` dataclass over raw dict**: Returning a plain `dict` from provider calls produces dynamic access patterns (`response["text"]`) that fail silently when a key is absent. A dataclass enforces a fixed interface at the definition site and raises `AttributeError` immediately if a field is missing during normalization.

**`stop_reason` normalization**: OpenAI uses `"stop"` and `"length"` as stop reasons; Anthropic uses `"end_turn"` and `"max_tokens"`. The abstraction layer maps both to a common set (`"stop"`, `"length"`) so application logic that checks stop reason does not need provider-specific branches.

**Conversation state as a `list[dict]` not a class**: Conversation history is structurally a list of messages. Wrapping it in a class adds lifecycle methods (trim, summarize, persist) that are useful but belong to application concerns, not the API client layer. The labs keep it as a plain list; production systems should add a dedicated class when history management logic grows beyond simple accumulation.

**Retry scope**: The retry handler wraps the abstraction call, not the SDK call. This means the retry logic is provider-agnostic — it does not need to know whether the underlying SDK is `openai` or `anthropic`. Provider-specific error types are caught by the abstraction layer and re-raised as a common `TransientAPIError` that the retry handler recognizes.

---

## 6. External Dependencies

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| `openai` Python SDK | Client for OpenAI and Ollama (compatible) | `light` |
| `anthropic` Python SDK | Client for Anthropic Messages API | `light` |
| Ollama | Local LLM runtime for offline development | `light` |
| OpenAI API | Cloud provider (requires `OPENAI_API_KEY`) | none (external) |
| Anthropic API | Cloud provider (requires `ANTHROPIC_API_KEY`) | none (external) |

---

## 7. Mapping to Labs

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| Direct OpenAI SDK call | `lab-openai-api` | Request structure, response parsing, usage metadata |
| Ollama OpenAI-compatible call | `lab-ollama-api` | `base_url` override, local model management |
| Anthropic SDK call | `lab-anthropic-api` | Schema differences, `content[0].text`, `stop_reason` |
| Streaming assembler | `lab-streaming` | Chunk accumulation, first-token latency, usage on stream |
| Retry + accumulator + abstraction | `lab-api-patterns` | Composed client with all three patterns together |

---

## 8. Trade-offs and Constraints

**Abstraction depth vs. feature access**: A thin abstraction covers the common case (text generation, usage tracking, stop reason). Accessing provider-specific features — Anthropic's extended thinking tokens, OpenAI's logprobs, Ollama's model metadata — requires either bypassing the abstraction or extending it. The current design accepts this as a constraint: the abstraction covers the 90% case, and provider-specific code is explicit when needed.

**Per-request message list cost**: The conversation accumulation pattern resends the full history on every request. A 50-turn conversation with 100 tokens per turn costs 5,000 prompt tokens on the 51st turn — the cost of turn 1 alone, repeated 50 times. Applications that need long-running sessions must implement trimming or summarization before this cost becomes prohibitive.

**Retry budget vs. user experience**: Three retries with doubling delay means a worst-case wait of 1 + 2 + 4 = 7 additional seconds before failing. For interactive UI applications, this may exceed the user's tolerance. Retry counts and delays must be tuned to the application's latency budget, not just network reliability.

---

## 9. Failure Modes

**Missing `stop_reason` check**: Returning `response.text` without checking `stop_reason == "length"` produces silently truncated responses. This is not a runtime error — the response is valid but incomplete. Applications that generate structured content (JSON, code) will silently produce unparseable output.

**Symmetric message assumption in Anthropic**: The Anthropic API requires strictly alternating `user`/`assistant` messages. A conversation accumulator that appends a `user` message without a preceding `assistant` reply — or that starts with `assistant` — raises a `400 Bad Request`. This is a design constraint, not a transient error; it should not be retried.

**Abstraction masking provider errors**: An abstraction layer that catches all exceptions and returns `None` or a default response prevents crashes but silently hides meaningful errors. Catch only known transient error types; let unknown errors propagate so they can be diagnosed.

---

## 10. Summary

The implementation maps five architecture components to concrete Python patterns: provider SDKs (`openai`, `anthropic`), a `ChatResponse` dataclass for schema normalization, a `list[dict]` for conversation accumulation, a `try/except` retry loop for transient failure handling, and a chunk-iteration loop for streaming. The key design decisions are: normalize stop reasons at the abstraction boundary, keep retry logic provider-agnostic, and keep conversation state as a plain list until lifecycle management requirements justify a class. All five patterns are exercised across the five labs in this module.
