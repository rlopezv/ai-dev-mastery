---
id: "memory-context-context-management"
title: "Context Management"
type: "topic"
step: "memory-context"
path: "docs/memory-context/context-management.md"
status: "draft"
level: "intermediate"

concepts:
  - "context management"
  - "sliding window"
  - "memory compression"
  - "summarization-based compression"
  - "token budget"

prerequisites:
  - "docs/memory-context/conversation-history.md"

next:
  - "docs/memory-context/external-memory.md"

related:
  - "docs/llm-fundamentals/context-window.md"
  - "docs/rag/context-assembly.md"

implementation_refs:
  - "labs/memory-context/lab-context-management"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes the strategies for keeping conversation history within the token budget — sliding window truncation, summarization-based compression, and hybrid approaches — and the trade-offs each introduces."
---

## 1. Intuition

A conversation accumulates turns. The context window does not grow. At some point, something
must be discarded or compressed. The question is not whether to manage context but which
strategy preserves the most useful signal for the fewest tokens.

---

## 2. Explanation

### 2.1 Why

Simple append-and-truncate — dropping the oldest turn whenever the budget is exceeded —
preserves recency but discards early context that may still be relevant: the user's stated
goal at turn 1, a constraint set at turn 3, or a decision made at turn 7. For short
conversations or tasks where recency is sufficient, this is the right choice. For longer
conversations where early context carries lasting importance, truncation alone loses
information that cannot be recovered without asking the user to repeat themselves.

Two strategies address this limitation: sliding window with configurable retention, and
summarization-based compression that distils prior turns into a compact summary that is
retained instead of the raw messages.

### 2.2 How

**Simple truncation.** Drop the oldest `user + assistant` pair when the budget is exceeded.
O(1) to execute; no additional API call required. Loses old context permanently.

**Sliding window.** Keep the last N complete turns regardless of token count, dropping
everything older. The window size is chosen to balance recency and budget. Unlike token-based
truncation, a fixed-turn window is predictable: a window of 10 turns is always 10 turns,
regardless of message length variation.

```python
def apply_sliding_window(history: list[dict], window_turns: int) -> list[dict]:
    # Each turn = 2 messages (user + assistant)
    max_messages = window_turns * 2
    return history[-max_messages:] if len(history) > max_messages else history
```

**Summarization-based compression.** When the history exceeds the budget, the application
sends the oldest N turns to the model with a summarization prompt and replaces those turns
with the resulting summary, stored as a synthetic `system` or `assistant` message. The
summary acts as a compressed record of the dropped context.

```python
# See: labs/memory-context/lab-context-management/main.py

SUMMARY_PROMPT = """Summarize the following conversation excerpt in 3-5 sentences.
Preserve: stated goals, decisions made, constraints mentioned, key facts established.
Discard: pleasantries, repetition, exploratory tangents.

{conversation_excerpt}"""

def compress_history(client, history: list[dict], turns_to_compress: int) -> list[dict]:
    old_turns = history[: turns_to_compress * 2]
    remaining = history[turns_to_compress * 2 :]

    excerpt = "\n".join(f"{m['role']}: {m['content']}" for m in old_turns)
    summary_text = call_model(client, SUMMARY_PROMPT.format(conversation_excerpt=excerpt))

    summary_message = {"role": "assistant",
                       "content": f"[Earlier conversation summary: {summary_text}]"}
    return [summary_message] + remaining
```

**Hybrid approach.** Maintain a rolling summary of older context and a full sliding window
of recent turns. The model always has access to the most recent N turns in full detail and
to a compressed record of everything before that. This is the most accurate strategy at the
cost of one additional API call per compression event.

### 2.3 Code example

```python
# See: labs/memory-context/lab-context-management/main.py

def manage_context(client, history: list[dict], budget: int) -> list[dict]:
    if count_tokens(history) <= budget:
        return history

    # Attempt summarization if history is long enough
    if len(history) >= 10:
        history = compress_history(client, history, turns_to_compress=5)

    # Fall back to sliding window if still over budget
    while count_tokens(history) > budget and len(history) >= 2:
        history = history[2:]

    return history
```

---

## 3. Strategy Comparison

| Strategy | Recency | Early context | Extra latency | Extra cost | Complexity |
|----------|---------|---------------|---------------|------------|------------|
| Simple truncation | Full | Lost | None | None | Low |
| Sliding window | Full | Lost | None | None | Low |
| Summarization | Full | Compressed | 1 API call | ~200–500 tokens | Medium |
| Hybrid (summary + window) | Full | Compressed | 1 API call | ~200–500 tokens | Medium-high |

---

## 4. Engineering Implications

**Compression events add latency.** A summarization call takes 300–800ms depending on
the number of turns being compressed and the model used. In an interactive chat application,
this delay is visible to the user. The compression trigger should be set conservatively —
before the last moment — so the compression can happen between turns rather than during one.

**Summary quality determines recall quality.** A poor summarization prompt produces a
summary that omits important facts. The prompt must explicitly direct the model to preserve
decisions, constraints, and stated goals — the signal that early turns carry. Generic
summarization ("summarize this conversation") reliably discards the most decision-relevant
content.

**Compression is irreversible.** Once the original turns are replaced by a summary, the
raw messages are gone. If the summary is inaccurate, the application cannot recover the
dropped context without replaying the conversation. For high-stakes applications where early
context must never be lost, external memory (persistent storage of all turns) is the only
safe strategy.

**Window size is not universal.** The right sliding window for a short-answer Q&A assistant
(5–8 turns) differs from the right window for a document editing session (20–30 turns) or a
multi-step planning conversation (full history with compression). The strategy must match
the conversation type, not a single default.

---

## 5. Implementation Connection

`lab-context-management` runs the same long conversation under all three strategies —
simple truncation, sliding window, and summarization — and measures recall accuracy by
asking a fact-checking question about early context at the end of each run. The lab makes
the information loss from truncation visible and quantifies the quality improvement from
summarization.

---

## 6. Failure Modes and Limitations

**Compression triggered too late.** If compression is triggered only when the budget is
already exceeded, the next API call may fail while the compression call is in progress.
The trigger threshold should be set at 80–90% of budget, leaving room to execute the
compression call without blocking the next user turn.

**Cascading compression loops.** If each compression call produces a summary long enough
to remain over budget, the application may enter a loop: compress → still over budget →
compress again. The compress function must enforce a hard maximum on summary length and
fall back to truncation if the summary itself exceeds it.

**User experience discontinuity.** When old context is silently replaced by a summary,
users who refer back to specific details from early in the conversation may receive answers
that contradict or miss those details. Some applications surface the compression event
explicitly ("I've summarized our earlier discussion to free up space") to set expectations.

---

## 7. Summary

Context management is the set of strategies that keep conversation history within the token
budget when the conversation grows beyond it. Simple truncation is zero-cost but loses early
context permanently. Sliding window is equally cheap but slightly more predictable. Summarization-based compression preserves early context in distilled form at the cost of one
additional API call per compression event. The hybrid strategy combines a rolling summary
with a full-detail window and provides the best recall accuracy for long conversations. The
right strategy depends on conversation type, latency tolerance, and whether early context
carries lasting importance.
