---
id: "lab-streaming"
title: "Streaming"
type: "lab-readme"
step: "llm-apis"
path: "labs/llm-apis/lab-streaming/README.md"
status: "draft"
level: "foundational"
concepts:
  - "streaming"
  - "first-token-latency"
  - "token-delta"
prerequisites:
  - "docs/llm-apis/streaming.md"
related:
  - "docs/llm-apis/README.md"
summary: "Implementation lab — measures batch vs streaming first-token latency, demonstrates chunk delta structure, and verifies that assembled streaming text matches the batch response."
---

# Streaming

## Navigation

[Labs](../../README.md) / [LLM APIs — Labs](../README.md) / Streaming

---

## Overview

This lab measures first-token latency in batch vs streaming mode, inspects the chunk delta structure of a streaming response, and assembles the full text from individual deltas to verify equivalence with the batch result.

**Out of scope:** retry logic (covered in `lab-api-patterns`), provider abstraction over streaming (covered in `lab-api-patterns`).

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `streaming` | `observe_latency_comparison()` — `stream=True` activates streaming mode; tokens are printed as they arrive instead of waiting for the full response |
| `first-token-latency` | `observe_latency_comparison()` — time to first chunk is recorded separately from total generation time and compared against batch mode |
| `token-delta` | `observe_chunk_structure()` — each chunk exposes `choices[0].delta.content` and `finish_reason`; the final chunk has `content=None` and `finish_reason` set |

---

## Setup

```bash
# Ollama must be running with llama3.2 loaded:
ollama serve
ollama pull llama3.2

# ANTHROPIC_API_KEY in .env is optional — skipped if absent
# Install dependencies (from the module root):
pip install -r labs/llm-apis/requirements.txt
```

---

## Run

```bash
cd labs/llm-apis
python lab-streaming/main.py
```

---

## Expected Output

```
=== Observation 1: Batch vs streaming latency (Ollama) ===
Batch mode:    X.XXs total  (NNN chars)

Streaming output:
<tokens appear progressively>

Streaming mode: X.XXs first-token  X.XXs total  (NNN chars)
Texts match:   True

=== Observation 2: Chunk delta structure (first 5 chunks) ===
Chunk 0: delta.content='The'    finish_reason=None
Chunk 1: delta.content=' color' finish_reason=None
...
Chunk N: delta.content=None     finish_reason='stop'

=== Observation 3: Anthropic streaming (text_stream iterator) ===
<tokens appear progressively>
Assembled length: NNN chars  Batch length: NNN chars
```

---

## What to observe

- **Observation 1:** streaming first-token time is a fraction of batch total time, while total generation times are similar. The perceived responsiveness difference is real even though throughput is unchanged.
- **Observation 2:** intermediate chunks have `finish_reason=None`; only the final chunk has `finish_reason` set and `delta.content=None`. Code that reads `content` without a `None` guard will fail on the last chunk.
- **Observation 3:** assembled text length from streaming should be close to the batch response length — any significant mismatch indicates truncated stream consumption.

---

## Concepts verified

- [ ] First-token latency is measurably shorter in streaming mode — observable at Observation 1
- [ ] Total generation time is approximately equal in both modes — observable at Observation 1
- [ ] Each chunk delivers a partial delta; the last chunk has `finish_reason` set — observable at Observation 2
- [ ] Assembled streaming text is equivalent to batch response text — observable at Observation 1

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_latency_comparison()`, add `break` inside the stream loop after collecting 5 chunks, before fully consuming the stream
- **Expected degradation:**
  - `assembled` is incomplete — only the first 5 tokens are captured
  - `Texts match: False` — truncated assembly does not match the full batch response
  - The underlying HTTP connection may remain open until the server closes it

Restore the complete stream loop after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM runtime — provides streaming via `stream=True` on the OpenAI-compatible endpoint |
| Anthropic API | Cloud LLM provider — optional; provides `text_stream` iterator; skipped if `ANTHROPIC_API_KEY` is absent |
