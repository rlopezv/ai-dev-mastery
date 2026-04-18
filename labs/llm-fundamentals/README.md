---
id: "llm-fundamentals-labs-readme"
title: "LLM Fundamentals — Labs"
type: "lab-readme"
step: "llm-fundamentals"
path: "labs/llm-fundamentals/README.md"
status: "draft"
level: "foundational"
concepts:
  - "inference-pipeline"
  - "tokenization"
  - "context-window"
  - "inference-parameters"
prerequisites:
  - "docs/llm-fundamentals/implementation-reference.md"
next:
  - "labs/llm-apis/README.md"
related:
  - "docs/llm-fundamentals/README.md"
implementation_refs:
  - "labs/llm-fundamentals/lab-llm-anatomy"
  - "labs/llm-fundamentals/lab-tokenization"
  - "labs/llm-fundamentals/lab-context-window"
  - "labs/llm-fundamentals/lab-inference-parameters"
validation_refs:
  - "meta/standards/validation/labs-checklist.md"
summary: "Four observation labs that make each stage of the LLM inference pipeline directly measurable using the Ollama API and tiktoken."
---

# LLM Fundamentals — Labs

## Navigation

[Labs](../README.md) / LLM Fundamentals — Labs

---


## 1. Overview

These labs implement four observation exercises, one per pipeline stage. Each lab isolates a single component of the LLM inference pipeline, sends controlled inputs, and prints measurable outputs that confirm the behavior described in the corresponding topic document.

No application is built. The purpose is direct verification: read a concept, run the lab, observe the prediction hold or fail.

**Not covered:**
- Fine-tuning or multimodality (concept-only topics, no labs)
- Multi-turn conversation management (covered in `memory-context`)
- Retrieval pipelines (covered in `rag`)

---

## 2. Lab Inventory

| Lab | Demonstrates | Type | Doc |
|-----|-------------|------|-----|
| `lab-llm-anatomy` | Transformer forward pass and autoregressive loop via Ollama API | observation | `llm-architecture.md` |
| `lab-tokenization` | Token encoding, boundary behavior, cross-language comparison | observation | `tokenization.md` |
| `lab-context-window` | Token budget arithmetic, component cost, limit behavior | observation | `context-window.md` |
| `lab-inference-parameters` | Sampling variance across temperature, top-k, and top-p | observation | `inference-parameters.md` |

---

## 3. Execution Model

All labs use the **`foundational` infrastructure profile**: Ollama running locally. No Docker, no vector database, no external API keys.

**Prerequisites:**

```bash
# 1. Install Ollama (https://ollama.com)
#    Then start the server:
ollama serve

# 2. Download the model used in the labs:
ollama pull llama3.2

# 3. Verify the model is available:
ollama list

# 4. Install Python dependencies (from the module root):
pip install -r labs/llm-fundamentals/requirements.txt
```

**Running a lab:**

```bash
cd labs/llm-fundamentals
cp .env.example .env          # edit if Ollama runs on a non-default port

python lab-llm-anatomy/main.py
python lab-tokenization/main.py
python lab-context-window/main.py
python lab-inference-parameters/main.py
```

Each lab prints its output to stdout. No server process needs to remain running between labs.

---

## 4. Lab Structure

```text
labs/llm-fundamentals/
├── README.md                        ← this file
├── .env.example                     ← environment variable template
├── requirements.txt                 ← Python dependencies
├── shared/
│   ├── __init__.py
│   └── client.py                    ← Ollama HTTP client wrapper
├── lab-llm-anatomy/
│   ├── README.md
│   └── main.py
├── lab-tokenization/
│   ├── README.md
│   └── main.py
├── lab-context-window/
│   ├── README.md
│   └── main.py
└── lab-inference-parameters/
    ├── README.md
    └── main.py
```

Each lab is self-contained. The only cross-lab dependency is `shared/client.py`, which provides the Ollama HTTP wrapper used by labs that call the API.

---

## 5. Mapping to Documentation

| Documentation | Lab |
|---------------|-----|
| `docs/llm-fundamentals/llm-architecture.md` | `lab-llm-anatomy` |
| `docs/llm-fundamentals/tokenization.md` | `lab-tokenization` |
| `docs/llm-fundamentals/context-window.md` | `lab-context-window` |
| `docs/llm-fundamentals/inference-parameters.md` | `lab-inference-parameters` |

Run each lab immediately after reading its corresponding topic document.

---

## 6. Validation

**lab-llm-anatomy**
```
Expected: Non-empty response string, prompt_eval_count > 0, eval_count > 0,
          prompt_eval_count is identical across 3 runs with the same prompt.
```

**lab-tokenization**
```
Expected: Token IDs printed as a list of integers, token count for Japanese
          input is higher than for the English equivalent, round-trip
          encode→decode reproduces the original string exactly.
```

**lab-context-window**
```
Expected: Token budget breakdown prints component costs; budget check
          correctly identifies whether the prompt fits; prompt_eval_count
          from the API matches the pre-send estimate within ±5 tokens.
```

**lab-inference-parameters**
```
Expected: Three runs at temperature=0 produce identical responses;
          three runs at temperature=1.0 produce at least two distinct responses;
          top_k=1 output is identical to temperature=0.
```

---

## 7. Common Issues

**Ollama not reachable.**
Each lab checks connectivity at startup and exits with a clear message if Ollama is not running. Start Ollama with `ollama serve` and retry.

**Model not found.**
The labs default to `llama3.2`. If the model is not downloaded, run `ollama pull llama3.2`. Set `MODEL=<other-model>` in `.env` to use a different model.

**Slow responses on CPU.**
Ollama uses GPU if available, CPU otherwise. CPU inference on a 3B parameter model takes 5–30 seconds per response. The labs are designed to work on CPU; reduce `num_predict` values in the `.env` if wait times are impractical.

**tiktoken token counts differ from Ollama's.**
`tiktoken` uses the OpenAI `cl100k_base` tokenizer. Llama3 uses a different tokenizer. Token counts will be close but not identical. This discrepancy is a learning point in `lab-tokenization`, not a bug.

---

## 8. Engineering Notes

**CPU latency for context-fill tests.** `lab-context-window` sends progressively longer prompts. On CPU, requests with 1,000+ input tokens can take 30–90 seconds. The lab caps input growth at 512 tokens by default; set `MAX_FILL_TOKENS` in `.env` to adjust.

**Model non-determinism at temperature > 0.** Output variation is expected and is the observable behavior being tested in `lab-inference-parameters`. If all three temperature=1.0 runs produce identical output, the model may be cached or the temperature is not being applied. Check that `options.temperature` appears in the request payload.

**`tiktoken` for standalone tokenization.** `lab-tokenization` requires no running server. The tokenizer runs entirely in-process. This is the only lab that can be run without Ollama.

---

## 9. Next Steps

After completing all four labs and passing the validation criteria in `docs/llm-fundamentals/validation.md`:

→ Proceed to [`labs/llm-apis/README.md`](../llm-apis/README.md)

If a lab produces unexpected behavior, consult the corresponding topic document's **Failure Modes** section before modifying the lab code.
