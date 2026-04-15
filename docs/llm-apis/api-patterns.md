---
id: "llm-apis-api-patterns"
title: "API Patterns"
type: "topic"
step: "llm-apis"
path: "docs/llm-apis/api-patterns.md"
status: "draft"
level: "foundational"

concepts:
  - "retry-with-backoff"
  - "conversation-accumulation"
  - "provider-abstraction"
  - "rate-limiting"

prerequisites:
  - "docs/llm-apis/openai-api.md"
  - "docs/llm-apis/ollama-api.md"
  - "docs/llm-apis/anthropic-api.md"
  - "docs/llm-apis/streaming.md"

next:
  - "docs/llm-apis/architecture.md"

related:
  - "docs/llm-apis/openai-api.md"
  - "docs/llm-apis/anthropic-api.md"

implementation_refs:
  - "labs/llm-apis/lab-api-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the recurring implementation patterns for LLM API clients — retry with exponential backoff, conversation history accumulation, and provider abstraction — that make API-level code production-grade."
---

## 1. Intuition

A single working API call is not application code — it is a script. Application code must handle failures, manage conversation state, and remain portable across providers. Three patterns cover most of what separates a one-off API call from a production-grade LLM client: retry with backoff for transient failures, message accumulation for multi-turn conversations, and a thin provider abstraction for portability.

---

## 2. Explanation

### 2.1 Why

LLM APIs fail in predictable ways: rate limits (`429`), temporary server overload (`500`/`503`), and network timeouts are all transient — retrying the same request after a pause succeeds. Without retry logic, these transient failures propagate as application errors, breaking user flows for recoverable conditions.

Conversation state is the application's responsibility because every API call is stateless. If the application does not append each exchange to the message history before the next call, the model has no memory of prior turns. This is the most common source of incoherent multi-turn behavior in early LLM applications.

Provider lock-in emerges when application code uses provider-specific response field paths and SDK idioms throughout. A thin abstraction layer — even just a wrapper function — localizes the provider-specific code, making it possible to switch providers or test against Ollama locally without modifying application logic.

### 2.2 How

**Retry with exponential backoff**

Transient API errors should be retried with increasing delays to avoid hammering a rate-limited endpoint:

```python
# See: labs/llm-apis/lab-api-patterns/main.py
import time
from openai import RateLimitError, APIStatusError

def call_with_retry(client, messages, model, max_retries=3):
    delay = 1.0
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500,
            )
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable")
```

The delay doubles on each retry (exponential backoff). Adding random jitter (`delay += random.uniform(0, 0.5)`) prevents synchronized retries from multiple clients hitting the rate limit simultaneously.

**Conversation accumulation**

Multi-turn conversations require appending each exchange to the message list before the next call:

```python
# See: labs/llm-apis/lab-api-patterns/main.py
messages = [{"role": "system", "content": "You are a helpful assistant."}]

def chat(client, model, user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model=model, messages=messages)
    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply
```

The message list grows with every turn. The caller is responsible for trimming or summarizing it before the context window limit is reached.

**Provider abstraction**

A minimal abstraction normalizes differences between providers into a common interface:

```python
# See: labs/llm-apis/lab-api-patterns/main.py
from dataclasses import dataclass

@dataclass
class ChatResponse:
    text: str
    input_tokens: int
    output_tokens: int

def call_openai(client, model, messages):
    r = client.chat.completions.create(model=model, messages=messages, max_tokens=500)
    return ChatResponse(
        text=r.choices[0].message.content,
        input_tokens=r.usage.prompt_tokens,
        output_tokens=r.usage.completion_tokens,
    )

def call_anthropic(client, model, system, messages):
    r = client.messages.create(model=model, system=system, messages=messages, max_tokens=500)
    return ChatResponse(
        text=r.content[0].text,
        input_tokens=r.usage.input_tokens,
        output_tokens=r.usage.output_tokens,
    )
```

Both functions return a `ChatResponse`. Application logic above this layer operates only on `ChatResponse` and does not know which provider was used.

---

## 3. Table

| Pattern | Problem solved | Implementation cost | When required |
|---------|---------------|--------------------|-|
| Retry with backoff | Transient API failures (rate limits, 5xx) | Low — wrapper function | Always in production; optional in labs |
| Conversation accumulation | Stateless API loses conversation context | Low — list append | Any multi-turn application |
| Provider abstraction | Provider lock-in; local vs cloud switching | Medium — normalization layer | Multi-provider apps; local dev + cloud prod |
| Rate limit tracking | Proactive avoidance before hitting limits | High — token counting + timing | High-volume production systems |

---

## 4. Engineering Implications

The retry pattern must distinguish between retryable and non-retryable errors. A `429 RateLimitError` is retryable. A `400 BadRequestError` from a malformed message is not — retrying immediately produces the same error. Catching all exceptions and retrying unconditionally wastes quota and masks bugs.

Conversation accumulation without a context budget check creates a slow leak: as conversations grow longer, prompt token costs increase and eventually the request exceeds the context window, producing a hard error. Applications that run long sessions must either trim old messages, summarize earlier turns, or set a maximum conversation depth.

The provider abstraction pattern works only if it captures the entire interface surface relevant to the application. If the application uses streaming in some paths and batch in others, the abstraction must handle both modes. A partial abstraction that covers batch but not streaming will still have provider-specific code paths, eliminating its portability benefit.

---

## 5. Implementation Connection

`lab-api-patterns` implements all three patterns against both Ollama and the Anthropic API. The retry pattern is tested by simulating rate limit errors. The conversation accumulation pattern runs a 5-turn conversation and verifies coherence. The provider abstraction pattern runs the same conversation through both providers and confirms that the calling code does not change.

---

## 6. Failure Modes and Limitations

**Retrying non-retryable errors**: Applying exponential backoff to a `400 Bad Request` caused by an invalid message structure retries 3 times, adds 7 seconds of delay, and then fails with the same error. Always inspect the error type before deciding to retry.

**Unbounded conversation history**: A naive accumulation loop that never trims the message list will eventually fail with a context window exceeded error — not on the first call, but after enough turns, making the bug difficult to reproduce in testing.

**Abstraction that leaks**: A provider abstraction that returns `None` for unsupported fields instead of raising an error allows provider-specific bugs to propagate silently. Abstractions should fail loudly at the boundary, not quietly downstream.

---

## 7. Summary

Three patterns make LLM API clients production-grade: retry with exponential backoff handles transient failures without propagating them to the application layer; conversation accumulation maintains coherent multi-turn state on the caller side; provider abstraction localizes schema differences and enables local-to-cloud portability. None of these patterns is optional in a real application — they are the minimum required to move from a working demo to a maintainable system.
