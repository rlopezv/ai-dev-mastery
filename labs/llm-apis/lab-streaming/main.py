# Lab: lab-streaming
# Module: llm-apis
# Doc reference: docs/llm-apis/streaming.md

import logging
import os
import sys
import time

import anthropic
import requests
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import ANTHROPIC_MODEL, MAX_TOKENS, OLLAMA_BASE_URL, OLLAMA_MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

PROMPT = "Explain what a context window is and why it matters for LLM applications."


def assert_ollama_ready() -> None:
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError):
        log.error("Ollama is not reachable at %s. Start it with: ollama serve", OLLAMA_BASE_URL)
        sys.exit(1)


def build_anthropic_client() -> anthropic.Anthropic | None:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        log.info("ANTHROPIC_API_KEY not set — skipping Anthropic streaming observation.")
        return None
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Observation 1 — batch vs streaming latency (Ollama)
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In observe_latency_comparison(), add "break" inside the stream loop
#   after collecting 5 chunks, before the stream is fully consumed
# - Observe:
#   * assembled text is incomplete — only the first ~5 tokens captured
#   * Texts match: False — truncated assembly diverges from batch response
#   * HTTP connection may remain open until server closes it

def observe_latency_comparison() -> None:
    """
    Compare time-to-first-output between batch and streaming modes.

    Concept: total generation time is identical; only first-token latency
    differs. Streaming makes the model feel responsive even for long outputs.
    """
    log.info("=== Observation 1: Batch vs streaming latency (Ollama) ===")

    client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    messages = [{"role": "user", "content": PROMPT}]

    # Batch mode — measure time to full response
    t0 = time.monotonic()
    batch_response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        stream=False,
    )
    batch_elapsed = time.monotonic() - t0
    batch_text = batch_response.choices[0].message.content

    log.info("Batch mode:    %.2fs total  (%d chars)", batch_elapsed, len(batch_text))

    # Streaming mode — measure time to first token
    t0 = time.monotonic()
    first_token_time = None
    assembled = ""

    stream = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        stream=True,
    )

    log.info("\nStreaming output:")
    for chunk in stream:
        # Concept: delta.content is the new token(s) in this chunk
        delta = chunk.choices[0].delta.content
        if delta:
            if first_token_time is None:
                first_token_time = time.monotonic() - t0
            print(delta, end="", flush=True)
            assembled += delta

    stream_total = time.monotonic() - t0
    print()  # newline after streamed output

    log.info(
        "\nStreaming mode: %.2fs first-token  %.2fs total  (%d chars)",
        first_token_time or 0,
        stream_total,
        len(assembled),
    )
    log.info("Texts match:   %s", batch_text.strip() == assembled.strip())


# ---------------------------------------------------------------------------
# Observation 2 — chunk delta structure
# ---------------------------------------------------------------------------

def observe_chunk_structure() -> None:
    """
    Print the raw structure of the first few chunks to inspect delta fields.

    Concept: each chunk has choices[0].delta.content with the new tokens;
    the last chunk has finish_reason set and content as None.
    """
    log.info("\n=== Observation 2: Chunk delta structure (first 5 chunks) ===")

    client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")

    stream = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": "Name three colors."}],
        max_tokens=30,
        stream=True,
    )

    for i, chunk in enumerate(stream):
        delta = chunk.choices[0].delta.content
        finish = chunk.choices[0].finish_reason
        log.info("Chunk %d: delta.content=%r  finish_reason=%r", i, delta, finish)
        if i >= 6:
            log.info("  ... (remaining chunks omitted)")
            # exhaust the stream silently
            for _ in stream:
                pass
            break


# ---------------------------------------------------------------------------
# Observation 3 — Anthropic text_stream iterator
# ---------------------------------------------------------------------------

def observe_anthropic_streaming(client: anthropic.Anthropic) -> None:
    """
    Stream a response from Anthropic and compare assembled text to batch output.

    Concept: Anthropic's SDK provides a .text_stream iterator that yields plain
    strings directly, abstracting away the SSE event types.
    """
    log.info("\n=== Observation 3: Anthropic streaming (text_stream iterator) ===")

    # Batch reference
    batch = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": PROMPT}],
    )
    batch_text = batch.content[0].text

    # Streaming — Concept: .text_stream yields str directly
    log.info("Streaming output:")
    assembled = ""
    with client.messages.stream(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": PROMPT}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            assembled += text

    print()
    log.info("\nAssembled length: %d chars  Batch length: %d chars", len(assembled), len(batch_text))
    log.info("Texts match (approx): %s", len(assembled) > 0 and len(batch_text) > 0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready()
    observe_latency_comparison()
    observe_chunk_structure()

    anthropic_client = build_anthropic_client()
    if anthropic_client:
        observe_anthropic_streaming(anthropic_client)

    log.info("\nDone. Review the observations against docs/llm-apis/streaming.md.")
