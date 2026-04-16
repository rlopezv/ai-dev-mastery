# Shared: context management strategies and prompt assembler
# Doc reference: docs/memory-context/context-management.md

from openai import OpenAI
from shared.config import MODEL, count_tokens, HISTORY_BUDGET


# ---------------------------------------------------------------------------
# Strategy: truncation
# ---------------------------------------------------------------------------

def apply_truncation(history: list[dict], budget: int = HISTORY_BUDGET) -> list[dict]:
    """
    Concept: truncation — drop oldest turn pairs until history fits in budget.

    Always removes complete pairs (user + assistant) to preserve role alternation.
    The most recent turns are retained.
    """
    result = list(history)
    while count_tokens(result) > budget and len(result) >= 2:
        result = result[2:]
    return result


# ---------------------------------------------------------------------------
# Strategy: sliding window
# ---------------------------------------------------------------------------

def apply_sliding_window(history: list[dict], window_pairs: int = 10) -> list[dict]:
    """
    Concept: sliding window — keep only the N most recent turn pairs.

    window_pairs controls how many user+assistant pairs are retained.
    Earlier turns are dropped regardless of token count.
    """
    # Each pair = 2 messages (user + assistant)
    keep = window_pairs * 2
    if len(history) <= keep:
        return list(history)
    # Ensure we cut on a pair boundary
    excess = len(history) - keep
    if excess % 2 != 0:
        excess += 1
    return history[excess:]


# ---------------------------------------------------------------------------
# Strategy: summarization-based compression
# ---------------------------------------------------------------------------

def compress_history(
    client: OpenAI,
    history: list[dict],
    keep_recent_pairs: int = 4,
) -> list[dict]:
    """
    Concept: summarization — compress older turns into a single summary message,
    keeping the most recent turns verbatim for recency continuity.

    Returns a new history: [summary_message] + recent_turns.
    The summary_message has role='user' and is prefixed so the model treats it
    as background context rather than a live question.
    """
    if len(history) <= keep_recent_pairs * 2:
        return list(history)

    boundary = len(history) - keep_recent_pairs * 2
    older_turns = history[:boundary]
    recent_turns = history[boundary:]

    # Concept: compression — ask the model to distill older turns into a summary
    conversation_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in older_turns
    )
    summary_prompt = (
        "Summarize the following conversation excerpt. "
        "Preserve all named entities, decisions, and facts that may be referenced later. "
        "Be concise.\n\n"
        + conversation_text
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": summary_prompt}],
    )
    summary_text = response.choices[0].message.content

    summary_message = {
        "role": "user",
        "content": f"[Earlier conversation summary]\n{summary_text}",
    }
    # Pair the summary with a minimal assistant acknowledgement to maintain alternation
    summary_ack = {
        "role": "assistant",
        "content": "Understood. I have the context from our earlier conversation.",
    }
    return [summary_message, summary_ack] + list(recent_turns)


# ---------------------------------------------------------------------------
# Prompt assembler
# ---------------------------------------------------------------------------

def assemble_messages(
    system_prompt: str,
    history: list[dict],
    memory_context: str | None = None,
) -> list[dict]:
    """
    Concept: context assembly — combine system prompt, optional retrieved memory,
    and conversation history into the final message list for the API call.

    memory_context, when provided, is appended to the system prompt so it is
    always visible regardless of history length.
    """
    full_system = system_prompt
    if memory_context:
        full_system = full_system + "\n\nRelevant context from memory:\n" + memory_context

    return [{"role": "system", "content": full_system}] + list(history)
