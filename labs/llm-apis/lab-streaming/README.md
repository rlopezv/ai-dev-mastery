# lab-streaming

**Module:** `llm-apis`
**Type:** implementation
**Doc:** `docs/llm-apis/streaming.md`
**Required:** yes

## What this lab demonstrates

- Batch vs streaming first-token latency comparison (Ollama)
- Chunk delta structure: `choices[0].delta.content`, `finish_reason`
- Text assembly from token deltas
- Anthropic `text_stream` iterator (if `ANTHROPIC_API_KEY` is set)
- Verification that assembled streaming text matches batch response

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `ANTHROPIC_API_KEY` in `.env` (optional — skipped if absent)
- `pip install -r labs/llm-apis/requirements.txt`

## Run

```bash
cd labs/llm-apis
python lab-streaming/main.py
```

## Expected output

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

## Concepts verified

- First-token latency is measurably shorter in streaming mode
- Total generation time is approximately equal in both modes
- Each chunk delivers a partial delta; the last chunk has `finish_reason` set
- Assembled streaming text is equivalent to batch response text
