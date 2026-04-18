---
id: "llm-apis-labs-readme"
title: "LLM APIs — Labs"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/README.md"
status: "draft"
level: "foundational"

concepts:
  - "chat-completion-api"
  - "openai-compatible-api"
  - "streaming"
  - "provider-abstraction"
  - "retry-with-backoff"
  - "conversation-accumulation"

prerequisites:
  - "docs/llm-apis/implementation-reference.md"

next:
  - "labs/prompt-engineering/README.md"

related:
  - "docs/llm-apis/README.md"

implementation_refs:
  - "labs/llm-apis/lab-openai-api"
  - "labs/llm-apis/lab-ollama-api"
  - "labs/llm-apis/lab-anthropic-api"
  - "labs/llm-apis/lab-streaming"
  - "labs/llm-apis/lab-api-patterns"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Five implementation labs that exercise API interaction with OpenAI, Ollama, and Anthropic — covering request/response mechanics, streaming, and the patterns that make LLM API clients production-grade."
---

# LLM APIs — Labs

## Navigation

[Labs](../README.md) / LLM APIs — Labs

---


## 1. Overview

These labs implement the API interaction patterns described in `docs/llm-apis/`. Each lab targets one provider or one cross-cutting pattern. Labs 1–4 are required; lab 5 is optional.

The progression moves from raw SDK calls (labs 1–3) to transport-level mechanics (lab 4) to composed application patterns (lab 5). Each lab can be run independently once the required environment variables are set.

**Not covered:**
- Prompt design strategies (see `prompt-engineering`)
- Structured outputs and function calling (see `structured-outputs`)
- Embeddings and retrieval (see `rag`)

---

## 2. Lab Inventory

| Lab | Demonstrates | Type | Required | Doc |
|-----|-------------|------|----------|-----|
| `lab-openai-api` | Chat Completions request structure, usage metadata, finish_reason | implementation | yes | `openai-api.md` |
| `lab-ollama-api` | OpenAI-compatible local call, native model management API | implementation | yes | `ollama-api.md` |
| `lab-anthropic-api` | Anthropic Messages API schema differences vs OpenAI | implementation | yes | `anthropic-api.md` |
| `lab-streaming` | Token delta accumulation, first-token latency measurement | implementation | yes | `streaming.md` |
| `lab-api-patterns` | Retry with backoff, conversation accumulation, provider abstraction | implementation | no | `api-patterns.md` |

---

## 3. Execution Model

All labs use the **`foundational` infrastructure profile**. Ollama runs locally. Cloud provider labs require API keys in the environment.

**Prerequisites:**

```bash
# 1. Start Ollama (must be running before lab-ollama-api and lab-streaming)
ollama serve
ollama pull llama3.2

# 2. Install Python dependencies (from the module root)
pip install -r labs/llm-apis/requirements.txt

# 3. Configure environment
cd labs/llm-apis
cp .env.example .env
# Edit .env — set OPENAI_API_KEY and ANTHROPIC_API_KEY for cloud labs
```

**Running a lab:**

```bash
cd labs/llm-apis
python lab-openai-api/main.py
python lab-ollama-api/main.py
python lab-anthropic-api/main.py
python lab-streaming/main.py
python lab-api-patterns/main.py   # optional
```

Each lab prints structured output to stdout. No server process is started or required to remain running between labs.

---

## 4. Lab Structure

```text
labs/llm-apis/
├── README.md                        ← this file
├── .env.example                     ← environment variable template
├── requirements.txt                 ← Python dependencies
├── shared/
│   ├── __init__.py
│   └── config.py                    ← shared environment variable loader
├── lab-openai-api/
│   ├── README.md
│   └── main.py
├── lab-ollama-api/
│   ├── README.md
│   └── main.py
├── lab-anthropic-api/
│   ├── README.md
│   └── main.py
├── lab-streaming/
│   ├── README.md
│   └── main.py
└── lab-api-patterns/
    ├── README.md
    └── main.py
```

Each lab is self-contained. The only cross-lab dependency is `shared/config.py`, which loads environment variables once via `python-dotenv`.

---

## 5. Mapping to Documentation

| Documentation | Lab |
|---------------|-----|
| `docs/llm-apis/openai-api.md` | `lab-openai-api` |
| `docs/llm-apis/ollama-api.md` | `lab-ollama-api` |
| `docs/llm-apis/anthropic-api.md` | `lab-anthropic-api` |
| `docs/llm-apis/streaming.md` | `lab-streaming` |
| `docs/llm-apis/api-patterns.md` | `lab-api-patterns` |

Run each lab immediately after reading its corresponding topic document.

---

## 6. Validation

**lab-openai-api**
```
Expected: response text is non-empty; usage.prompt_tokens > 0;
          usage.completion_tokens > 0; finish_reason printed;
          3-turn conversation produces coherent replies.
```

**lab-ollama-api**
```
Expected: OpenAI-SDK call returns identical structure to lab-openai-api;
          /api/tags lists at least one model; /api/show returns model metadata
          with parameter_size field populated.
```

**lab-anthropic-api**
```
Expected: response text read from content[0].text; usage.input_tokens > 0;
          stop_reason is "end_turn"; alternating-message conversation coherent;
          schema diff table printed showing field name differences vs OpenAI.
```

**lab-streaming**
```
Expected: tokens print progressively to stdout during generation;
          assembled text matches batch response for the same prompt;
          time-to-first-token is measurably shorter in streaming mode;
          Anthropic text_stream produces same assembled text as batch call.
```

**lab-api-patterns**
```
Expected: retry handler succeeds on 3rd attempt after 2 injected failures;
          5-turn conversation maintains coherent context throughout;
          ChatResponse returned from both providers has identical structure.
```

---

## 7. Common Issues

**`OPENAI_API_KEY` not set.**
`lab-openai-api` and `lab-api-patterns` (OpenAI path) will raise `AuthenticationError`. Set the key in `.env` or export it in the shell before running.

**`ANTHROPIC_API_KEY` not set.**
`lab-anthropic-api` and `lab-api-patterns` (Anthropic path) will raise `AuthenticationError`. Same fix.

**Ollama not reachable.**
`lab-ollama-api` and `lab-streaming` check connectivity at startup and exit with a clear message. Start Ollama with `ollama serve` and ensure the model is pulled.

**Model not found in Ollama.**
Default model is `llama3.2`. If not downloaded: `ollama pull llama3.2`. Set `OLLAMA_MODEL` in `.env` to use a different model.

**Streaming prints nothing then exits.**
The terminal must support cursor movement. If running in a non-interactive shell or redirecting stdout, streaming output may be buffered. Add `flush=True` to `print` calls (already included in the labs).

---

## 8. Engineering Notes

**API keys are read from environment only.** Never hard-code keys. The `.env` file is gitignored. The `.env.example` file contains variable names with empty values and is safe to commit.

**Cloud provider labs incur cost.** `lab-openai-api` and `lab-anthropic-api` make real API calls. Each lab run consumes fewer than 500 tokens total at the smallest available models (`gpt-4o-mini`, `claude-haiku-4-5-20251001`). Cost is negligible but not zero.

**Streaming latency comparison is hardware-dependent.** On a fast network with OpenAI, first-token latency is typically 200–600ms. With Ollama on CPU, it may be 1–5 seconds. The lab measures and prints actual latency; absolute values are informational.

**`lab-api-patterns` injects artificial failures.** The retry demonstration raises `RateLimitError` manually on the first two calls to simulate rate limiting without actually exhausting API quota. This is the only lab that uses mocking.

---

## 9. Next Steps

After completing the required labs and passing the criteria in `docs/llm-apis/validation.md`:

→ Proceed to [`labs/prompt-engineering/README.md`](../prompt-engineering/README.md)

If a lab produces unexpected output, consult the **Failure Modes** section of the corresponding topic document before modifying the lab code.
