# LLM API Design Patterns

LLM APIs expose a request-response interface over HTTP. The caller sends a prompt,
the provider runs inference, and the result is returned synchronously or as a stream.
Designing robust LLM-backed services requires handling the specific failure modes and
throughput constraints of LLM inference: high latency, token-based rate limits,
stochastic outputs, and long-running requests.

## Request Structure

The dominant API format is the OpenAI Chat Completions structure:

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.7,
  "max_tokens": 256
}
```

The `messages` array is the stateful interface: the caller maintains conversation
history by appending prior assistant responses to each subsequent request. The API
is stateless — the provider does not store history between calls.

## Streaming

Streaming returns token deltas over a persistent HTTP connection as they are generated,
using the `text/event-stream` content type (server-sent events). The caller receives
partial responses with sub-500ms first-token latency, regardless of total response length.

Without streaming, the caller waits for the full response before receiving anything.
For responses over 1000 tokens, this can exceed 10 seconds on cloud APIs, degrading
perceived responsiveness.

Streaming events follow the format:

```
data: {"choices": [{"delta": {"content": "The "}, "finish_reason": null}]}
data: {"choices": [{"delta": {"content": "capital"}, "finish_reason": null}]}
data: {"choices": [{"delta": {}, "finish_reason": "stop"}]}
data: [DONE]
```

The stream terminates when `[DONE]` is received. The complete response is reconstructed
by concatenating all `content` deltas before the `[DONE]` event.

## Rate Limiting

LLM APIs enforce two types of rate limits:

- **Requests per minute (RPM)**: the number of HTTP requests allowed per minute.
  Typical tiers: 500–5000 RPM for paid plans, 3–60 RPM for free tiers.
- **Tokens per minute (TPM)**: the total input + output tokens consumed per minute.
  Typical tiers: 500K–10M TPM for paid plans.

When a rate limit is exceeded, the API returns HTTP 429 with a `Retry-After` header
specifying the wait duration.

## Retry with Exponential Backoff

Transient errors — rate limits, 5xx errors, connection timeouts — are recoverable by
retrying after a delay. Exponential backoff with jitter is the standard strategy:

```
delay = min(base * 2^attempt + random(0, 1), max_delay)
```

Parameters:
- `base`: initial delay in seconds (typically 1.0)
- `attempt`: zero-indexed retry count
- `max_delay`: ceiling to prevent indefinite growth (typically 60s)
- `jitter`: random fraction to prevent thundering herd from simultaneous retries

After a 429 response, respect the `Retry-After` header value as the minimum delay.
After a 5xx response, apply exponential backoff starting from 2 seconds.

Do not retry 4xx errors (except 429): they indicate invalid requests that will not
succeed regardless of retry timing.

## Context Window Management

Each model has a context window — the maximum tokens it can process in one call.
Context windows range from 4096 tokens (older models) to 1 million tokens (Gemini 1.5).

Token consumption per call:
- Input tokens: system prompt + conversation history + current user message + tool schemas
- Output tokens: model response + any tool call arguments

For multi-turn applications, conversation history grows with each turn. A session of
20 turns with 200 tokens per turn consumes 4000 tokens of input context — before
the system prompt or current message. Context management strategies:

1. Sliding window: retain only the last N turns.
2. Summarization: replace old turns with a compressed summary.
3. Selective retention: keep only turns flagged as important.

## Tool Calling

Tool calling allows the model to emit a structured function invocation instead of a
text response. The caller declares available tools in the request; the model decides
whether and which to invoke; the caller executes the tool and returns the result.

Tool declaration format:
```json
{
  "type": "function",
  "function": {
    "name": "search_documents",
    "description": "Search the document corpus for relevant information.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "The search query"}
      },
      "required": ["query"]
    }
  }
}
```

The model's tool call response contains the function name and JSON-serialized arguments.
The caller executes the function, appends the result as a `tool` role message, and
calls the model again. The loop continues until `finish_reason = "stop"` (no tool call).

## Async Patterns for Long-Running Requests

For requests that may exceed HTTP timeout limits or where clients may disconnect:

- **Task queue pattern**: the caller submits a request to a job queue (Celery, ARQ),
  receives a job ID immediately, and polls a `/status/{id}` endpoint for completion.
- **Webhook pattern**: the caller provides a callback URL; the server calls it when
  generation completes. No polling required, but the caller must expose an endpoint.
- **Server-sent events with reconnection**: the server streams partial results over SSE
  and tracks a `Last-Event-ID` so clients can resume after disconnection.

The synchronous request-response model fails when generation time exceeds HTTP gateway
timeouts (typically 30–60 seconds) or when the client is a mobile app that can
disconnect mid-response.

## Prompt Caching

Several providers cache the key-value (KV) attention states of the input prompt and
reuse them across requests that share the same prefix. Anthropic's prompt caching reduces
input token cost by ~90% and latency by ~85% for requests with a shared system prompt.

Effective caching requires that the cacheable prefix (system prompt, few-shot examples,
large context documents) appears first in the message list and does not change between
requests. Variable user input must always follow the cacheable prefix.
