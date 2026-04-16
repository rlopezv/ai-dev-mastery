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

## What to observe

- **Observation 1:** streaming first-token time is a fraction of batch total time, while total generation times are similar. The perceived responsiveness difference is real even though throughput is unchanged.
- **Observation 2:** intermediate chunks have `finish_reason=None`; only the final chunk has `finish_reason` set and `delta.content=None`. Code that reads `content` without a `None` guard will fail on the last chunk.
- Assembled text length from streaming should be close to the batch response length.

---

## Concepts verified

- [ ] First-token latency is measurably shorter in streaming mode
- [ ] Total generation time is approximately equal in both modes
- [ ] Each chunk delivers a partial delta; the last chunk has `finish_reason` set
- [ ] Assembled streaming text is equivalent to batch response text

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_latency_comparison()`, add `break` inside the stream loop after collecting 5 chunks, before fully consuming the stream
- **Expected degradation:**
  - `assembled` is incomplete — only the first 5 tokens are captured
  - `Texts match: False` — truncated assembly does not match the full batch response
  - The underlying HTTP connection may remain open until the server closes it

Restore the complete stream loop after the experiment.
