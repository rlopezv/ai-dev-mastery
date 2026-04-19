---
id: "lab-ollama-api"
title: "Ollama API"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/lab-ollama-api/README.md"
status: "draft"
level: "foundational"
concepts:
  - "openai-compatible-api"
  - "local-llm-runtime"
prerequisites:
  - "docs/llm-apis/ollama-api.md"
related:
  - "docs/llm-apis/README.md"
summary: "Implementation lab — demonstrates Ollama's OpenAI-compatible interface via base_url override, native model management endpoints, and the difference between native and compatible response shapes."
---

# Ollama API

## Navigation

[Labs](../../README.md) / [LLM APIs — Labs](../README.md) / Ollama API

---

## Overview

This lab targets Ollama as both an OpenAI-compatible endpoint and a native HTTP server. It shows that only a `base_url` change is needed to redirect the OpenAI SDK to Ollama, and it exposes model management and response shape differences that are only visible via the native API.

**Out of scope:** streaming (covered in `lab-streaming`), provider abstraction across multiple backends (covered in `lab-api-patterns`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `openai-compatible-api` | `observe_openai_compatible_call()` — OpenAI SDK with `base_url="http://localhost:11434/v1"` and `api_key="ollama"`; response field paths are identical to a real OpenAI call |
| `local-llm-runtime` | `observe_model_listing()` / `observe_model_metadata()` — native `/api/tags` and `/api/show` endpoints expose model management not available in the compatible interface |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# Install dependencies (from the module root):
pip install -r labs/llm-apis/requirements.txt
```

---

## Run

```bash
cd labs/llm-apis
python lab-ollama-api/main.py
```

---

## Expected Output

```
=== Observation 1: OpenAI-compatible call via SDK ===
Model:    llama3.2
Response: <answer>
Usage:    prompt=NN  completion=NN

=== Observation 2: Native model listing (/api/tags) ===
Downloaded models (N):
  llama3.2:latest                          XXXX MB

=== Observation 3: Model metadata (/api/show) ===
Model family:    llama
Parameter size:  3.2B
Quantization:    Q4_K_M
Format:          gguf

=== Observation 4: Native /api/chat response shape ===
Native path:    data['message']['content']
OpenAI path:    response.choices[0].message.content
Response text:  <answer>
```

---

## What to observe

- **Observation 1:** response field paths (`choices[0].message.content`, `usage.prompt_tokens`) are identical to a real OpenAI call — only the URL changes.
- **Observation 3:** metadata fields (`family`, `parameter_size`, `quantization_level`) are only available via native `/api/show`. There is no equivalent in the OpenAI-compatible interface.
- **Observation 4:** native `/api/chat` puts text at `data["message"]["content"]`; OpenAI-compatible wraps it in `choices[0].message.content`. These are different paths for the same content.

---

## Concepts verified

- [ ] `base_url` + `api_key="ollama"` is the only change needed to redirect OpenAI SDK to Ollama — observable at Observation 1
- [ ] Native endpoints (`/api/tags`, `/api/show`) provide model management not available via compatible interface — observable at Observations 2 and 3
- [ ] Native `/api/chat` and OpenAI-compatible interface return the same content at different paths — observable at Observation 4

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_native_chat_format()`, replace `data["message"]["content"]` with `data["choices"][0]["message"]["content"]`
- **Expected degradation:**
  - `KeyError: 'choices'` — the native Ollama format has no `choices` wrapper
  - Shows that the native and OpenAI-compatible paths are mutually exclusive: code written for one format fails silently or crashes on the other

Restore the native path after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — serves both OpenAI-compatible (`/v1/chat/completions`) and native (`/api/chat`, `/api/tags`, `/api/show`) endpoints |
