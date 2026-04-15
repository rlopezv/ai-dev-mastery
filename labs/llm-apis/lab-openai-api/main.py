# Lab: lab-openai-api
# Module: llm-apis
# Doc reference: docs/llm-apis/openai-api.md

import logging
import os
import sys

from openai import AuthenticationError, OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import MAX_TOKENS, OPENAI_MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def build_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        log.error("OPENAI_API_KEY is not set. Add it to .env and retry.")
        sys.exit(1)
    return OpenAI(api_key=api_key)


# ---------------------------------------------------------------------------
# Observation 1 — basic chat completion
# ---------------------------------------------------------------------------

def observe_basic_completion(client: OpenAI) -> None:
    """
    Send a single-turn request and inspect the full response structure.

    Concept: the response wraps generated text in choices[0].message.content
    alongside usage metadata and a finish_reason signal.
    """
    log.info("=== Observation 1: Basic chat completion ===")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise technical assistant."},
            {"role": "user", "content": "What is a context window in one sentence?"},
        ],
        max_tokens=80,
    )

    # Concept: text lives at choices[0].message.content
    text = response.choices[0].message.content
    finish = response.choices[0].finish_reason

    log.info("Model:         %s", response.model)
    log.info("Response:      %s", text)
    log.info("finish_reason: %s", finish)
    log.info(
        "Usage:         prompt=%d  completion=%d  total=%d",
        response.usage.prompt_tokens,
        response.usage.completion_tokens,
        response.usage.total_tokens,
    )


# ---------------------------------------------------------------------------
# Observation 2 — finish_reason: length
# ---------------------------------------------------------------------------

def observe_truncation(client: OpenAI) -> None:
    """
    Force a truncated response by setting max_tokens very low.

    Concept: finish_reason='length' signals that the response was cut off,
    not that the model finished. Callers must check this field.
    """
    log.info("\n=== Observation 2: Forced truncation (finish_reason=length) ===")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "user", "content": "Explain how transformers work in detail."},
        ],
        max_tokens=10,
    )

    text = response.choices[0].message.content
    finish = response.choices[0].finish_reason

    log.info("Response (truncated): %r", text)
    log.info("finish_reason:        %s", finish)

    # Concept: application code must act on finish_reason='length'
    if finish == "length":
        log.info("WARNING: response was cut off — increase max_tokens or summarise the prompt.")


# ---------------------------------------------------------------------------
# Observation 3 — multi-turn conversation
# ---------------------------------------------------------------------------

def observe_multi_turn(client: OpenAI) -> None:
    """
    Run a 3-turn conversation by accumulating messages between calls.

    Concept: the API is stateless — the full message history must be resent
    on every call so the model can maintain coherence across turns.
    """
    log.info("\n=== Observation 3: Multi-turn conversation ===")

    messages = [
        {"role": "system", "content": "You are a concise technical assistant."},
    ]
    turns = [
        "What is temperature in LLM inference?",
        "How does it differ from top-p sampling?",
        "Which one should I use for a code generation task?",
    ]

    for i, user_input in enumerate(turns, 1):
        # Concept: append user message before each call
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
        )

        reply = response.choices[0].message.content

        # Concept: append assistant reply so the next call includes it
        messages.append({"role": "assistant", "content": reply})

        log.info("Turn %d — User:      %s", i, user_input)
        log.info("Turn %d — Assistant: %s", i, reply[:200])
        log.info("         prompt_tokens so far: %d", response.usage.prompt_tokens)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        client = build_client()
        observe_basic_completion(client)
        observe_truncation(client)
        observe_multi_turn(client)
        log.info("\nDone. Review the observations against docs/llm-apis/openai-api.md.")
    except AuthenticationError:
        log.error("Invalid OPENAI_API_KEY. Check the value in .env.")
        sys.exit(1)
