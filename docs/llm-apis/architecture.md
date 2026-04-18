---
id: "llm-apis-architecture"
title: "LLM APIs — Architecture"
type: "architecture"
step: "llm-apis"
path: "docs/llm-apis/architecture.md"
status: "draft"
level: "foundational"

concepts:
  - "chat-completion-api"
  - "openai-compatible-api"
  - "provider-abstraction"
  - "streaming"
  - "api-client"

prerequisites:
  - "docs/llm-apis/README.md"
  - "docs/llm-apis/openai-api.md"
  - "docs/llm-apis/ollama-api.md"
  - "docs/llm-apis/anthropic-api.md"
  - "docs/llm-apis/streaming.md"
  - "docs/llm-apis/api-patterns.md"

next:
  - "docs/llm-apis/implementation-reference.md"

related:
  - "docs/llm-fundamentals/architecture.md"
  - "docs/prompt-engineering/README.md"

implementation_refs:
  - "labs/llm-apis/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the system-level structure of an LLM API client — providers, client layer, abstraction, and conversation state — and how these components interact across batch and streaming call paths."
---

# LLM APIs — Architecture

## Navigation

[Docs](../README.md) / [LLM APIs](README.md) / LLM APIs — Architecture

---

## 1. System Overview

The system described in this step is an application-layer LLM client: the set of components an application needs to make calls to LLM providers, manage conversation state, and handle failures. The client sits between application logic and provider HTTP endpoints. It does not include model internals, infrastructure management, or prompt design — those are addressed in other modules.

The core engineering challenge is that providers have different schemas, applications need stateful conversations over a stateless API, and transient failures must not propagate to users. The architecture isolates each concern in a distinct component.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| Provider SDK | Transport layer | Serializes requests, deserializes responses, manages HTTP connections |
| Abstraction layer | Normalization | Maps provider-specific schemas to a common response structure |
| Conversation manager | State | Accumulates and trims the message list between turns |
| Retry handler | Resilience | Intercepts transient errors and retries with exponential backoff |
| LLM provider | External service | Runs model inference and returns generated text |

---

## 3. Component Interactions

The **abstraction layer** wraps the **provider SDK**. Application logic calls the abstraction; the abstraction selects the correct SDK method, translates the request, and normalizes the response. The **conversation manager** owns the message list and updates it after each exchange; it calls the abstraction, not the SDK directly. The **retry handler** wraps the abstraction call — it does not need to know which provider is in use.

```
Application logic
    │
    ▼
Conversation manager  ──► message list (stateful)
    │
    ▼
Retry handler  ──► catches RateLimitError, APIStatusError (5xx)
    │
    ▼
Abstraction layer  ──► normalizes request/response schema
    │
    ├──► OpenAI SDK  ──► OpenAI / Ollama endpoint
    └──► Anthropic SDK  ──► Anthropic endpoint
```

---

## 4. Data Flow

**Batch call path**:

```text
User input
  │
  ▼
Conversation manager: append {"role": "user", "content": input}
  │
  ▼
Retry handler: attempt call
  │
  ▼
Abstraction layer: translate to provider schema
  │
  ▼
Provider SDK: POST /v1/chat/completions or /v1/messages
  │
  ▼
Provider: run inference, return full response
  │
  ▼
Abstraction layer: normalize → ChatResponse(text, input_tokens, output_tokens)
  │
  ▼
Conversation manager: append {"role": "assistant", "content": text}
  │
  ▼
Application logic: receives ChatResponse
```

**Streaming call path**:

```text
User input
  │
  ▼  [same steps to provider]
Provider: run inference, emit token deltas via SSE
  │
  ▼
Provider SDK: yields chunks as iterator
  │
  ▼
Application logic: iterates chunks, assembles full text
  │
  ▼
Conversation manager: append assembled text as assistant message
```

Streaming bypasses the abstraction layer's response normalization because the response is assembled chunk by chunk. The full text is normalized into the message history after stream completion.

---

## 5. Execution Flow

1. Application calls `conversation_manager.chat(user_input)`
2. Conversation manager appends user message to history
3. Conversation manager calls `retry_handler.call(messages)`
4. Retry handler calls `abstraction_layer.complete(messages)`
5. Abstraction layer selects provider SDK and translates schema
6. SDK serializes and sends HTTP request
7. Provider processes and returns response
8. Abstraction layer normalizes response to `ChatResponse`
9. Retry handler returns `ChatResponse` (or retries on transient error)
10. Conversation manager appends assistant reply to history
11. Application receives `ChatResponse`

Decision point at step 9: if the error is `RateLimitError` or `APIStatusError` with 5xx status, retry with backoff. If `BadRequestError` (4xx other than 429), raise immediately.

---

## 6. Integration Points

| System | Integration point | Direction |
|--------|-------------------|-----------|
| OpenAI API | `openai` SDK → `https://api.openai.com/v1` | Outbound |
| Ollama | `openai` SDK → `http://localhost:11434/v1` | Outbound (local) |
| Anthropic API | `anthropic` SDK → `https://api.anthropic.com/v1` | Outbound |
| Application layer | Abstraction layer interface | Internal |
| `prompt-engineering` module | System prompt construction | Upstream dependency |
| `structured-outputs` module | Tool call request fields | Downstream extension |

---

## 7. Trade-offs and Design Decisions

**Single abstraction vs. provider-native code**: The abstraction layer adds indirection and a normalization step. The benefit is portability — a single application can switch between Ollama and OpenAI by changing a configuration value. The cost is that provider-specific features (Anthropic's extended thinking, OpenAI's structured outputs) require extending the abstraction or bypassing it. The architecture accepts this cost because provider portability is more valuable than feature completeness at this stage.

**Stateful conversation manager vs. caller-managed history**: Embedding conversation state in a manager object simplifies call sites but ties the manager to a single conversation thread. Multi-session applications that need to manage multiple concurrent conversations must either instantiate one manager per conversation or extend the manager to key by conversation ID. The labs use a single-conversation manager; production extensions must account for concurrency.

**Retry at the abstraction boundary vs. SDK-level retry**: The OpenAI and Anthropic SDKs include built-in retry logic. Explicit retry handling in the architecture gives the application control over which errors are retried, how many times, and with what backoff schedule. SDK defaults may not align with application requirements (e.g. a pipeline where a 5-second retry timeout is too long).

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| Provider SDK — OpenAI/Ollama | `lab-openai-api`, `lab-ollama-api` |
| Provider SDK — Anthropic | `lab-anthropic-api` |
| Streaming path | `lab-streaming` |
| Retry handler + conversation manager + abstraction layer | `lab-api-patterns` |

---

## 9. Limitations and Boundaries

This architecture covers single-model, single-provider API calls. It does not address:

- Multi-model routing (sending different request types to different models)
- Parallel API calls for batch processing (concurrent request management)
- Token counting before a call to preemptively avoid context window errors
- Prompt construction logic (see `prompt-engineering`)
- Structured output parsing and function call execution (see `structured-outputs`)
- Cost tracking and budget enforcement across sessions

---

## 10. Summary

The LLM API client architecture has five components: provider SDK (transport), abstraction layer (schema normalization), conversation manager (stateful history), retry handler (transient failure recovery), and the LLM provider (external inference). Data flows from application logic through the conversation manager and retry handler, is translated by the abstraction layer, transmitted by the SDK, and normalized on return. Streaming bypasses response normalization and requires the application to assemble text before updating conversation history. The abstraction layer is the key design decision — it enables provider portability at the cost of feature completeness.
