---
id: "llm-apis-ollama-api"
title: "Ollama API"
type: "topic"
step: "llm-apis"
path: "docs/llm-apis/ollama-api.md"
status: "draft"
level: "foundational"

concepts:
  - "openai-compatible-api"
  - "local-llm-runtime"
  - "model-management"

prerequisites:
  - "docs/llm-apis/openai-api.md"

next:
  - "docs/llm-apis/anthropic-api.md"

related:
  - "docs/llm-apis/streaming.md"
  - "docs/llm-apis/api-patterns.md"

implementation_refs:
  - "labs/llm-apis/lab-ollama-api"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how Ollama exposes a local LLM runtime with an OpenAI-compatible API, enabling development without cloud API keys, and how to manage models through its native endpoints."
---

# Ollama API

## Navigation

[Docs](../README.md) / [LLM APIs](README.md) / Ollama API

---

## 1. Intuition

Ollama is a local process that downloads and serves open-weight LLMs on your machine. It exposes an HTTP API on `localhost:11434`. Two interfaces exist side by side: a native Ollama API and an OpenAI-compatible endpoint at `/v1/`. The OpenAI-compatible endpoint means any code written against the OpenAI Python SDK runs against Ollama by changing one URL and removing the API key requirement.

---

## 2. Explanation

### 2.1 Why

Developing against a cloud LLM API during the early stages of a project creates unnecessary friction: every run incurs cost, requires an internet connection, and exposes potentially sensitive test data to a third-party service. Ollama removes these constraints by running open-weight models (Llama, Mistral, Gemma) locally, making the development loop free, offline-capable, and private.

The OpenAI-compatible interface is a deliberate design choice that maximizes adoption. It means existing tooling, SDKs, and application code written for OpenAI need no modification to run against Ollama — only the `base_url` and `api_key` parameters of the client change. This portability is valuable: local development uses Ollama, production uses a cloud provider, and the application logic does not change.

### 2.2 How

Ollama runs as a background service. When a request arrives, it loads the requested model into memory if not already loaded, runs inference, and streams or returns the response. Models are stored locally after being pulled from the Ollama registry.

**OpenAI-compatible interface** (`/v1/chat/completions`):

```python
# See: labs/llm-apis/lab-ollama-api/main.py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",          # required by SDK but not validated by Ollama
)

response = client.chat.completions.create(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is a context window?"},
    ],
)

reply = response.choices[0].message.content
```

The only differences from the OpenAI call are `base_url` and `api_key`. Response structure is identical.

**Native Ollama API** (`/api/`):

Ollama also exposes its own endpoints for model management and direct generation:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tags` | GET | List downloaded models |
| `/api/pull` | POST | Download a model |
| `/api/show` | POST | Inspect model metadata |
| `/api/chat` | POST | Chat with a model (Ollama-native format) |
| `/api/generate` | POST | Raw text completion (no message roles) |

The native `/api/chat` format differs slightly from OpenAI's — `message` uses the same role schema but the response wraps the content differently. Use the OpenAI-compatible endpoint unless you need model management operations, which are only available natively.

### 2.3 Model management

Models are pulled once and cached locally. The `OLLAMA_MODEL` environment variable in the lab infrastructure defaults to `llama3.2`. The `ollama-init` container in `docker-compose.yml` handles the pull automatically when the stack starts.

---

## 3. Table

| Interface | Endpoint | SDK | When to use |
|-----------|----------|-----|-------------|
| OpenAI-compatible | `/v1/chat/completions` | `openai` Python SDK | Application code; portability between providers |
| Ollama native chat | `/api/chat` | `requests` or `httpx` | When OpenAI SDK is not available or not desirable |
| Ollama native generate | `/api/generate` | `requests` or `httpx` | Raw completion without role structure |
| Model management | `/api/tags`, `/api/pull`, `/api/show` | `requests` or `httpx` | Listing, downloading, and inspecting models |

---

## 4. Engineering Implications

Ollama loads models into RAM (or VRAM if a GPU is available). A 7B model in 4-bit quantization requires approximately 4–5 GB of memory. If the host machine does not have enough free RAM, Ollama will fail to load the model or will fall back to CPU-only inference with significantly degraded throughput. The docker-compose configuration sets `OLLAMA_MEMORY_LIMIT` to cap resource usage.

The `OLLAMA_KEEP_ALIVE` parameter controls how long a loaded model stays in memory after the last request. The default in the infrastructure is `24h`. A short keep-alive reduces idle memory usage but adds cold-start latency (5–30 seconds for large models) on the first request of a new session.

Model identifiers in Ollama use the format `name:tag` (e.g. `llama3.2:latest`). The `:latest` suffix is implied when omitted. Requesting a model that has not been pulled raises a 404 error — not a graceful fallback.

---

## 5. Implementation Connection

`lab-ollama-api` demonstrates both interfaces: using the OpenAI SDK with `base_url` override, and using `requests` directly against the native Ollama endpoints. It also exercises model listing and metadata inspection via the management API. Ollama must be running before the lab executes — the lab does not start it.

---

## 6. Failure Modes and Limitations

**Model not found**: If the requested model has not been pulled, Ollama returns HTTP 404. This is not caught by the OpenAI SDK as a model error — it raises an `APIStatusError`. Always verify that models are available before running application code in a new environment.

**Cold-start latency**: The first request after a model load takes several seconds. This is not an error but will cause timeouts if client code has a short deadline. Labs configure a generous timeout; production callers must do the same.

**Response quality gap**: Open-weight models at the 7B–13B scale perform significantly below GPT-4-class models on complex reasoning tasks. Code that works correctly against a cloud provider may produce incorrect or incomplete results locally. This is expected — Ollama is a development and learning tool, not a production substitute.

---

## 7. Summary

Ollama runs open-weight LLMs locally and exposes an OpenAI-compatible REST API, making it a zero-cost, offline-capable development target. Code written against the OpenAI Python SDK requires only a `base_url` change to switch from a cloud provider to Ollama. Native Ollama endpoints add model management operations not available in the OpenAI-compatible interface. Memory availability and model pull status are the two operational preconditions that must be verified before use.
