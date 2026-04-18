# Lab: lab-tokenization
# Module: llm-fundamentals
# Doc reference: docs/llm-fundamentals/tokenization.md

import logging

import tiktoken

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# Concept: cl100k_base is the GPT-4 tokenizer — not the same as Llama3's,
# but sufficient to observe the BPE mechanics described in the topic doc.
ENCODING_NAME = "cl100k_base"


# ---------------------------------------------------------------------------
# Observation 1 — encode and decode round-trip
# ---------------------------------------------------------------------------

def observe_round_trip(text: str, enc: tiktoken.Encoding) -> None:
    """Encode text, print token IDs, decode back, confirm lossless round-trip."""
    log.info("=== Observation 1: Round-trip encode → decode ===")
    log.info("Input:   %r", text)

    # Concept: tokenization converts text to a flat list of integer token IDs
    token_ids = enc.encode(text)
    log.info("IDs:     %s", token_ids)
    log.info("Count:   %d tokens", len(token_ids))

    # Concept: decoding is deterministic and lossless
    decoded = enc.decode(token_ids)
    log.info("Decoded: %r", decoded)

    if decoded == text:
        log.info("✓ Round-trip is lossless")
    else:
        log.info("✗ Round-trip differs — investigate encoding")


# ---------------------------------------------------------------------------
# Observation 2 — token count comparison across input types
# ---------------------------------------------------------------------------

def observe_token_counts(enc: tiktoken.Encoding) -> None:
    """
    Compare token counts for different input types.

    Concept: token boundaries are corpus-statistical, not linguistic.
    English prose is most efficient; non-Latin text and rare words cost more tokens.
    """
    log.info("\n=== Observation 2: Token count by input type ===")

    samples = [
        ("English — common words",     "The transformer architecture uses self-attention."),
        ("English — rare word",        "antidisestablishmentarianism"),
        ("Spanish",                    "La arquitectura transformer usa auto-atención."),
        ("Japanese",                   "トランスフォーマーアーキテクチャは自己注意を使用します。"),
        ("Python code",                "def encode(text: str) -> list[int]: ..."),
        ("Numbers / date",             "2024-04-15 at 09:30:00"),
        ("URL",                        "https://example.com/api/v1/embeddings?model=text"),
        ("JSON fragment",              '{"role": "user", "content": "Hello"}'),
    ]

    for label, text in samples:
        ids = enc.encode(text)
        log.info("  %-35s → %3d tokens  %r", label, len(ids), text[:50])


# ---------------------------------------------------------------------------
# Observation 3 — leading space changes the token ID
# ---------------------------------------------------------------------------

def observe_leading_space(enc: tiktoken.Encoding) -> None:
    """
    Show that 'Paris' and ' Paris' encode to different token IDs.

    Concept: tokenizers include surrounding whitespace in the token.
    String concatenation without a space produces unexpected token splits.
    """
    log.info("\n=== Observation 3: Leading space changes token ID ===")
    for word in ("Paris", " Paris", "paris", " paris"):
        ids = enc.encode(word)
        log.info("  %r → %s", word, ids)


# ---------------------------------------------------------------------------
# Observation 4 — a single character change cascades through tokenization
# ---------------------------------------------------------------------------

def observe_character_sensitivity(enc: tiktoken.Encoding) -> None:
    """
    Modify one character in a word and observe the token sequence change.

    Concept: BPE merge rules are applied left-to-right; one character change
    can invalidate all merges in a pre-token, producing a completely different
    token sequence.
    """
    log.info("\n=== Observation 4: Character sensitivity ===")
    base = "tokenization"
    for variant in (base, base + "s", base + "!", base.upper()):
        ids = enc.encode(variant)
        log.info("  %r → %s  (%d tokens)", variant, ids, len(ids))


# ---------------------------------------------------------------------------
# Observation 5 — token budget estimate for a sample prompt
# ---------------------------------------------------------------------------

# --------------------------------------------------
# FAILURE CASE
# --------------------------------------------------
# Failure case:
# - In observe_budget_estimate(), set max_output = 0
# - Observe:
#   * All three context limits report "fits: yes" even for prompts
#     that would overflow at runtime
#   * Simulates forgetting to reserve output tokens in the budget

def observe_budget_estimate(enc: tiktoken.Encoding) -> None:
    """
    Compute the token cost of a realistic prompt before sending it to an API.

    Concept: cost is per token, not per word or character. Always tokenize
    before estimating API cost or checking context window fit.
    """
    log.info("\n=== Observation 5: Budget estimate for a sample prompt ===")
    system = "You are a helpful assistant. Answer concisely."
    user = (
        "Explain the difference between fine-tuning and retrieval-augmented generation "
        "in the context of enterprise software architecture."
    )
    max_output = 256

    system_tokens = len(enc.encode(system))
    user_tokens   = len(enc.encode(user))
    total_input   = system_tokens + user_tokens
    grand_total   = total_input + max_output

    log.info("  System prompt:   %d tokens", system_tokens)
    log.info("  User message:    %d tokens", user_tokens)
    log.info("  Total input:     %d tokens", total_input)
    log.info("  Max output:      %d tokens", max_output)
    log.info("  Grand total:     %d tokens", grand_total)

    for limit in (2048, 4096, 8192):
        fits = grand_total <= limit
        log.info("  Fits in %d-token context: %s", limit, "yes" if fits else "no")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    enc = tiktoken.get_encoding(ENCODING_NAME)
    log.info("Tokenizer: %s\n", ENCODING_NAME)

    observe_round_trip("The quick brown fox jumps over the lazy dog.", enc)
    observe_token_counts(enc)
    observe_leading_space(enc)
    observe_character_sensitivity(enc)
    observe_budget_estimate(enc)

    log.info("\nDone. Compare token counts with docs/llm-fundamentals/tokenization.md §3.")
