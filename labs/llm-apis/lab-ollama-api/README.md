---
id: "lab-ollama-api"
title: "Ollama API"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/lab-ollama-api/README.md"
status: "draft"
level: "foundational"
concepts:
  - "openai-compatible-interface"
  - "local-inference"
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

**Module:** `llm-apis`
**Type:** implementation
**Doc:** `docs/llm-apis/ollama-api.md`
**Required:** yes

## What this lab demonstrates

- OpenAI SDK call against Ollama with `base_url` override
- Response structure identity with OpenAI (same field paths)
- Native Ollama model listing via `/api/tags`
- Model metadata inspection via `/api/show`
- Native `/api/chat` response shape vs OpenAI-compatible shape

## Prerequisites

- Ollama running locally: `ollama serve`
- Model downloaded: `ollama pull llama3.2`
- `pip install -r labs/llm-apis/requirements.txt`

## Run

```bash
cd labs/llm-apis
python lab-ollama-api/main.py
```

## Expected output

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

## What to observe

- **Observation 1:** response field paths (`choices[0].message.content`, `usage.prompt_tokens`) are identical to a real OpenAI call — only the URL changes.
- **Observation 3:** metadata fields (`family`, `parameter_size`, `quantization_level`) are only available via native `/api/show`. There is no equivalent in the OpenAI-compatible interface.
- **Observation 4:** native `/api/chat` puts text at `data["message"]["content"]`; OpenAI-compatible wraps it in `choices[0].message.content`. These are different paths for the same content.

---

## Concepts verified

- [ ] `base_url` + `api_key="ollama"` is the only change needed to redirect OpenAI SDK to Ollama
- [ ] Native endpoints (`/api/tags`, `/api/show`) provide model management not available via compatible interface
- [ ] Native `/api/chat` and OpenAI-compatible interface return the same content at different paths

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_native_chat_format()`, replace `data["message"]["content"]` with `data["choices"][0]["message"]["content"]`
- **Expected degradation:**
  - `KeyError: 'choices'` — the native Ollama format has no `choices` wrapper
  - Shows that the native and OpenAI-compatible paths are mutually exclusive: code written for one format fails silently or crashes on the other

Restore the native path after the experiment.
