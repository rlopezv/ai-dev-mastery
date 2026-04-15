# Lab: lab-anthropic-api
# Module: llm-apis
# Doc reference: docs/llm-apis/anthropic-api.md

import logging
import os
import sys

import anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import ANTHROPIC_MODEL, MAX_TOKENS

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def build_client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        log.error("ANTHROPIC_API_KEY is not set. Add it to .env and retry.")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Observation 1 — basic Messages API call
# ---------------------------------------------------------------------------

def observe_basic_call(client: anthropic.Anthropic) -> None:
    """
    Send a single-turn request and inspect the Anthropic response structure.

    Concept: system is a top-level field (not a role in messages),
    and response text lives at content[0].text — not choices[0].message.content.
    """
    log.info("=== Observation 1: Basic Messages API call ===")

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=80,                   # Concept: required field — no default
        system="You are a concise technical assistant.",   # Concept: top-level field
        messages=[
            {"role": "user", "content": "What is a context window in one sentence?"},
        ],
    )

    # Concept: text is at content[0].text, not choices[0].message.content
    text = response.content[0].text
    stop = response.stop_reason          # Concept: "end_turn" not "stop"

    log.info("Model:       %s", response.model)
    log.info("Response:    %s", text)
    log.info("stop_reason: %s", stop)   # "end_turn" = normal completion
    log.info(
        "Usage:       input=%d  output=%d",
        response.usage.input_tokens,     # Concept: "input_tokens" not "prompt_tokens"
        response.usage.output_tokens,    # Concept: "output_tokens" not "completion_tokens"
    )


# ---------------------------------------------------------------------------
# Observation 2 — multi-turn conversation with strict alternation
# ---------------------------------------------------------------------------

def observe_multi_turn(client: anthropic.Anthropic) -> None:
    """
    Run a 3-turn conversation respecting the user/assistant alternation requirement.

    Concept: Anthropic messages must strictly alternate user/assistant.
    Sending two consecutive user messages raises a 400 Bad Request.
    """
    log.info("\n=== Observation 2: Multi-turn conversation (strict alternation) ===")

    messages = []
    turns = [
        "What is temperature in LLM inference?",
        "How does it differ from top-p sampling?",
        "Which one should I use for a code generation task?",
    ]

    for i, user_input in enumerate(turns, 1):
        messages.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=MAX_TOKENS,
            system="You are a concise technical assistant.",
            messages=messages,
        )

        reply = response.content[0].text
        messages.append({"role": "assistant", "content": reply})

        log.info("Turn %d — User:      %s", i, user_input)
        log.info("Turn %d — Assistant: %s", i, reply[:200])
        log.info("         input_tokens so far: %d", response.usage.input_tokens)


# ---------------------------------------------------------------------------
# Observation 3 — schema comparison with OpenAI
# ---------------------------------------------------------------------------

def observe_schema_diff(client: anthropic.Anthropic) -> None:
    """
    Print the concrete field differences between Anthropic and OpenAI schemas.

    Concept: these differences mean API-level code is not portable between
    providers without a normalization layer.
    """
    log.info("\n=== Observation 3: Schema comparison — Anthropic vs OpenAI ===")

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=60,
        system="You are a concise technical assistant.",
        messages=[{"role": "user", "content": "Define tokenization briefly."}],
    )

    log.info("%-30s  %-35s  %s", "Aspect", "OpenAI path", "Anthropic path")
    log.info("%-30s  %-35s  %s", "-" * 28, "-" * 33, "-" * 33)
    log.info(
        "%-30s  %-35s  %s",
        "Response text",
        "choices[0].message.content",
        "content[0].text",
    )
    log.info(
        "%-30s  %-35s  %s",
        "Input token count",
        "usage.prompt_tokens",
        "usage.input_tokens",
    )
    log.info(
        "%-30s  %-35s  %s",
        "Output token count",
        "usage.completion_tokens",
        "usage.output_tokens",
    )
    log.info(
        "%-30s  %-35s  %s",
        "Normal stop signal",
        'finish_reason = "stop"',
        'stop_reason = "end_turn"',
    )
    log.info(
        "%-30s  %-35s  %s",
        "System prompt location",
        "messages[0] role=system",
        "system= (top-level field)",
    )
    log.info("\nActual values from this response:")
    log.info("  content[0].text:          %r", response.content[0].text[:60])
    log.info("  usage.input_tokens:       %d", response.usage.input_tokens)
    log.info("  usage.output_tokens:      %d", response.usage.output_tokens)
    log.info("  stop_reason:              %s", response.stop_reason)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        client = build_client()
        observe_basic_call(client)
        observe_multi_turn(client)
        observe_schema_diff(client)
        log.info("\nDone. Review the observations against docs/llm-apis/anthropic-api.md.")
    except anthropic.AuthenticationError:
        log.error("Invalid ANTHROPIC_API_KEY. Check the value in .env.")
        sys.exit(1)
