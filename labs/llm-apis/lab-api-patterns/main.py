# Lab: lab-api-patterns
# Module: llm-apis
# Doc reference: docs/llm-apis/api-patterns.md

import logging
import os
import sys
import time
from dataclasses import dataclass

import anthropic
from openai import OpenAI, RateLimitError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import ANTHROPIC_MODEL, MAX_TOKENS, OLLAMA_BASE_URL, OLLAMA_MODEL

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared data structure — provider abstraction
# ---------------------------------------------------------------------------

@dataclass
class ChatResponse:
    """
    Normalized response structure.

    Concept: a common return type across providers decouples application logic
    from provider-specific field paths and SDK idioms.
    """
    text: str
    input_tokens: int
    output_tokens: int
    stop_reason: str  # normalized: "stop" | "length"


# ---------------------------------------------------------------------------
# Provider factory functions
# ---------------------------------------------------------------------------

def call_ollama(client: OpenAI, messages: list[dict]) -> ChatResponse:
    """
    Concept: Ollama uses the OpenAI-compatible interface — base_url is the only
    difference from a real OpenAI call.
    """
    r = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )
    # Concept: normalize stop reason to a common vocabulary
    raw_stop = r.choices[0].finish_reason
    stop = "length" if raw_stop == "length" else "stop"

    return ChatResponse(
        text=r.choices[0].message.content,
        input_tokens=r.usage.prompt_tokens,
        output_tokens=r.usage.completion_tokens,
        stop_reason=stop,
    )


def call_anthropic(client: anthropic.Anthropic, system: str, messages: list[dict]) -> ChatResponse:
    """
    Concept: Anthropic requires system as a top-level field and returns text
    at content[0].text with differently named usage fields.
    The abstraction normalizes all of this into ChatResponse.
    """
    r = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages,
    )
    # Concept: normalize Anthropic stop reasons
    raw_stop = r.stop_reason
    stop = "length" if raw_stop == "max_tokens" else "stop"

    return ChatResponse(
        text=r.content[0].text,
        input_tokens=r.usage.input_tokens,
        output_tokens=r.usage.output_tokens,
        stop_reason=stop,
    )


# ---------------------------------------------------------------------------
# Observation 1 — retry with exponential backoff
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In observe_retry_with_backoff(), change:
#     except RateLimitError:
#   to:
#     except ValueError:
# - Observe:
#   * injected RateLimitError is not caught — propagates immediately on attempt 1
#   * no retry occurs; backoff logic never runs
#   * shows that retry handlers must enumerate specific error types —
#     a broad except Exception would mask non-retryable errors

def observe_retry_with_backoff() -> None:
    """
    Demonstrate retry logic by injecting artificial RateLimitError on the
    first two attempts, succeeding on the third.

    Concept: transient errors (429, 5xx) should be retried with increasing
    delays. Non-transient errors (400) must not be retried.
    """
    log.info("=== Observation 1: Retry with exponential backoff ===")

    ollama_client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    attempt_count = 0

    def flaky_call(messages: list[dict]) -> ChatResponse:
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count <= 2:
            # Concept: simulate transient rate limit failure
            log.info("  [Attempt %d] Injecting RateLimitError...", attempt_count)
            raise RateLimitError(
                message="Simulated rate limit",
                response=None,   # type: ignore[arg-type]
                body=None,
            )
        log.info("  [Attempt %d] Call succeeds.", attempt_count)
        return call_ollama(ollama_client, messages)

    messages = [{"role": "user", "content": "What is temperature in LLMs?"}]
    delay = 1.0
    max_retries = 4
    result = None

    for attempt in range(max_retries):
        try:
            result = flaky_call(messages)
            break
        except RateLimitError:
            if attempt == max_retries - 1:
                log.error("All %d retries exhausted.", max_retries)
                raise
            log.info("  Waiting %.1fs before retry...", delay)
            time.sleep(delay)
            delay *= 2  # Concept: exponential backoff

    if result:
        log.info("Final response: %s", result.text[:150])
        log.info("stop_reason:    %s", result.stop_reason)


# ---------------------------------------------------------------------------
# Observation 2 — conversation accumulation
# ---------------------------------------------------------------------------

def observe_conversation_accumulation() -> None:
    """
    Run a 5-turn conversation using explicit message list accumulation.

    Concept: the API is stateless; the caller appends each exchange to the
    message list before the next request. Token cost grows with each turn.
    """
    log.info("\n=== Observation 2: Conversation accumulation (5 turns) ===")

    ollama_client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    system = "You are a concise technical assistant."
    messages = [{"role": "system", "content": system}]

    turns = [
        "What is a transformer?",
        "What role does self-attention play in it?",
        "How does that relate to the context window?",
        "Can the model attend to tokens outside the context window?",
        "Summarise our conversation in one sentence.",
    ]

    for i, user_input in enumerate(turns, 1):
        messages.append({"role": "user", "content": user_input})
        response = call_ollama(ollama_client, messages)
        messages.append({"role": "assistant", "content": response.text})

        log.info("Turn %d  input_tokens=%-4d  Q: %s", i, response.input_tokens, user_input)
        log.info("        reply: %s", response.text[:180])

    log.info("\nToken cost grew from turn 1 to turn 5: compare input_tokens above.")


# ---------------------------------------------------------------------------
# Observation 3 — provider abstraction
# ---------------------------------------------------------------------------

def observe_provider_abstraction() -> None:
    """
    Send the same question to Ollama and Anthropic through the abstraction layer.

    Concept: calling code operates only on ChatResponse — it does not know
    which provider produced the result.
    """
    log.info("\n=== Observation 3: Provider abstraction ===")

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        log.info("ANTHROPIC_API_KEY not set — running Ollama side only.")
        anthropic_client = None
    else:
        anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

    ollama_client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    system = "You are a concise technical assistant."
    question = "What is the difference between temperature and top-p in LLM inference?"
    messages = [{"role": "user", "content": question}]

    def run_and_print(provider_name: str, response: ChatResponse) -> None:
        """Concept: identical call site regardless of which provider was used."""
        log.info(
            "[%s]  input=%d  output=%d  stop=%s",
            provider_name,
            response.input_tokens,
            response.output_tokens,
            response.stop_reason,
        )
        log.info("Response: %s\n", response.text[:200])

    ollama_response = call_ollama(ollama_client, messages)
    run_and_print("Ollama", ollama_response)

    if anthropic_client:
        anthropic_response = call_anthropic(anthropic_client, system, messages)
        run_and_print("Anthropic", anthropic_response)

    log.info("Both responses are ChatResponse instances — caller code is identical.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    observe_retry_with_backoff()
    observe_conversation_accumulation()
    observe_provider_abstraction()
    log.info("\nDone. Review the observations against docs/llm-apis/api-patterns.md.")
