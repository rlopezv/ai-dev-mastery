---
id: "llm-apis-streaming"
title: "Streaming"
type: "topic"
step: "llm-apis"
path: "docs/llm-apis/streaming.md"
status: "draft"
level: "foundational"

concepts:
  - "streaming"
  - "server-sent-events"
  - "token-delta"
  - "first-token-latency"

prerequisites:
  - "docs/llm-apis/openai-api.md"
  - "docs/llm-apis/ollama-api.md"

next:
  - "docs/llm-apis/api-patterns.md"

related:
  - "docs/llm-apis/anthropic-api.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/llm-apis/lab-streaming"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how LLM APIs deliver token-by-token responses over persistent HTTP connections using Server-Sent Events, and what changes on the client side when switching from batch to streaming mode."
---

# Streaming

## Navigation

[Docs](../README.md) / [LLM APIs](README.md) / Streaming

---

## 1. Intuition

Without streaming, an API call blocks until the model has generated the entire response — a wait of several seconds for a long reply. With streaming, the model sends each generated token immediately, so the client starts receiving output within milliseconds of the first token being produced. The user sees text appearing progressively, which makes a 10-second generation feel interactive rather than frozen.

---

## 2. Explanation

### 2.1 Why

LLM generation is autoregressive: the model produces one token at a time. Each token requires a full forward pass through the network. A 300-token response represents 300 sequential forward passes before a batch response returns anything. Streaming exposes this natural cadence directly to the client — instead of buffering all 300 tokens on the server and transmitting them at once, the server sends each token as it is produced.

The engineering motivation is latency perception, not throughput. The total generation time is identical with or without streaming. What changes is the first token latency — the time from request sent to first output received. Streaming first token latency is typically under 500ms; batch response latency grows with response length. For UI applications, streaming is the expected behavior. For batch processing or log analysis, batch mode simplifies downstream handling.

### 2.2 How

Streaming is implemented via **Server-Sent Events (SSE)**: a standard HTTP mechanism where the server writes a sequence of `data:` lines to an open connection rather than closing it after a single response. Each line contains a JSON chunk. The client reads chunks as they arrive and accumulates them.

**OpenAI / Ollama streaming**:

```python
# See: labs/llm-apis/lab-streaming/main.py
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

stream = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Explain context windows briefly."}],
    stream=True,
)

full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
        full_response += delta
```

Each `chunk` contains a `delta` object with `content` set to the new token(s). The final chunk has `finish_reason` set and `content` as `None`.

**Anthropic streaming**:

```python
# See: labs/llm-apis/lab-streaming/main.py
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    messages=[{"role": "user", "content": "Explain context windows briefly."}],
) as stream:
    full_response = ""
    for text in stream.text_stream:
        print(text, end="", flush=True)
        full_response += text
```

Anthropic's SDK provides a `.text_stream` iterator that yields plain strings directly, abstracting away the SSE event types.

### 2.3 Chunk structure comparison

| Provider | SDK stream access | Delta field path | Text yield |
|----------|------------------|-----------------|------------|
| OpenAI | `stream = client.chat.completions.create(stream=True)` | `chunk.choices[0].delta.content` | May be `None` on last chunk |
| Ollama | Same as OpenAI (compatible interface) | Same as OpenAI | Same as OpenAI |
| Anthropic | `client.messages.stream(...)` context manager | `stream.text_stream` iterator | Yields `str` directly |

---

## 3. Table

| Mode | First token latency | Client complexity | Response assembly | Use case |
|------|--------------------|--------------------|-------------------|----------|
| Batch | Seconds (grows with length) | Low — single response object | None required | Batch pipelines, log processing |
| Streaming | Milliseconds | Higher — chunk accumulation | Required | UI applications, interactive tools |

---

## 4. Engineering Implications

Streaming changes the response lifecycle in ways that affect downstream code. With batch mode, `response.choices[0].message.content` is a complete string. With streaming, the application must accumulate chunks before the full content is available. This affects:

- **Token usage**: OpenAI does not include `usage` metadata in streaming chunks by default. Accumulated token counts are only available if `stream_options={"include_usage": True}` is set. Anthropic provides usage on the final event.
- **Error handling**: Errors mid-stream manifest as exceptions during iteration, not as a failed initial response. A try/except block around the stream loop is required.
- **Logging**: Log the assembled response after the stream closes, not during — logging partial chunks produces noisy, out-of-order entries.

---

## 5. Implementation Connection

`lab-streaming` demonstrates streaming against all three providers in the lab infrastructure. For Ollama, the lab compares the time-to-first-token between streaming and batch mode for the same prompt to make the latency difference observable. It also shows the chunk accumulation pattern and the difference between Anthropic's text iterator and OpenAI's delta model.

---

## 6. Failure Modes and Limitations

**Connection interruption**: A streaming response is an open HTTP connection. Network interruptions during a long generation produce a partial response with no error on the already-received chunks. The application must detect a prematurely closed stream (e.g. incomplete sentence, missing `finish_reason`) and decide whether to retry.

**No usage by default (OpenAI)**: Omitting `stream_options={"include_usage": True}` on OpenAI streaming calls means `usage` is `None` in all chunks. Code that reads usage metadata to track costs will silently receive nothing.

**Buffering in intermediate layers**: HTTP proxies, reverse proxies, and some web frameworks buffer SSE streams before forwarding them, negating the latency benefit. Streaming only works end-to-end if every intermediary passes chunks through without buffering.

---

## 7. Summary

Streaming transmits tokens as they are generated over an open HTTP connection using Server-Sent Events. First token latency drops from seconds to milliseconds; total generation time is unchanged. The client must accumulate chunks to reconstruct the full response. OpenAI and Ollama use identical streaming interfaces; Anthropic provides a higher-level text iterator that simplifies accumulation. Error handling, usage tracking, and connection interruption require explicit handling that batch mode does not.
