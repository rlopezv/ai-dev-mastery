---
id: "memory-context-conversation-history"
title: "Conversation History"
type: "topic"
step: "memory-context"
path: "docs/memory-context/conversation-history.md"
status: "draft"
level: "intermediate"

concepts:
  - "conversation history"
  - "conversation accumulation"
  - "history truncation"
  - "sliding window"
  - "token budget"

prerequisites:
  - "docs/memory-context/memory-types.md"
  - "docs/llm-apis/api-patterns.md"
  - "docs/llm-fundamentals/context-window.md"

next:
  - "docs/memory-context/context-management.md"

related:
  - "docs/llm-apis/openai-api.md"
  - "docs/memory-context/context-management.md"

implementation_refs:
  - "labs/memory-context/lab-conversation-history"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how to build and manage a stateful conversation history over a stateless API, including accumulation strategy, token counting, and the point at which truncation becomes necessary."
---

# Conversation History

## Navigation

[Docs](../README.md) / [Memory and Context Management](README.md) / Conversation History

---

## 1. Intuition

A chat completion API call is like a letter: you send the full conversation every time, and
the server responds without remembering any prior letters. To create the illusion of a
continuous conversation, the application must include every prior exchange in each new
letter — until the letter gets too long and something has to be left out.

---

## 2. Explanation

### 2.1 Why

The chat completion API is stateless by design. This simplifies the server: it maintains no
session state, can scale horizontally, and treats every request independently. The cost is
transferred to the caller: the application is responsible for maintaining the conversation
state and deciding how much of it to include in each request.

This design creates a tension. A longer history gives the model more context for accurate,
coherent responses. A longer history also consumes more of the context window, leaving less
space for system prompts, retrieved documents, and the expected output. The history list is
not a free resource — every token in it competes with every other token for space.

### 2.2 How

**Accumulation.** Each turn appends two messages to a list: the user message and the
assistant reply. Before each API call, the full list is passed as the `messages` parameter.
The model sees the entire exchange and can refer to any prior turn directly.

```python
history.append({"role": "user", "content": user_message})
response = client.chat.completions.create(model=MODEL, messages=system_messages + history)
assistant_reply = response.choices[0].message.content
history.append({"role": "assistant", "content": assistant_reply})
```

**Token counting.** The history's token cost grows by roughly `len(user_message_tokens) +
len(assistant_reply_tokens) + 4` per turn (the 4 accounts for message role and separator
overhead in the chat format). The application must track this total to know when the budget
is approaching the limit.

Most provider SDKs do not expose a built-in token counter for a message list. The standard
approach is to use the tokenizer associated with the model:

```python
# See: labs/memory-context/lab-conversation-history/main.py
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4")

def count_tokens(messages: list[dict]) -> int:
    total = 0
    for msg in messages:
        total += 4  # role + framing overhead
        total += len(encoder.encode(msg["content"]))
    return total + 2  # reply priming
```

For Ollama-served models, the same tiktoken library can be used as an approximation since
most open-weight models use compatible tokenizers.

**Budget ceiling.** The application sets a maximum token budget for the history before
each call. A common formula is:

```text
history_budget = context_window - system_prompt_tokens - output_reservation - safety_margin
```

Where `output_reservation` is the expected maximum output length and `safety_margin` is
typically 10–15% of the context window to absorb token count approximation errors.

**Truncation trigger.** When `count_tokens(history) > history_budget`, the application
must reduce the history before making the next call. The simplest strategy is to drop the
oldest message pair. More sophisticated strategies are covered in `context-management.md`.

### 2.3 Code example

```python
# See: labs/memory-context/lab-conversation-history/main.py

CONTEXT_WINDOW = 8192
OUTPUT_RESERVATION = 512
SAFETY_MARGIN = 400
SYSTEM_TOKENS = count_tokens(SYSTEM_MESSAGES)
HISTORY_BUDGET = CONTEXT_WINDOW - SYSTEM_TOKENS - OUTPUT_RESERVATION - SAFETY_MARGIN

def enforce_budget(history: list[dict]) -> list[dict]:
    # Drop oldest pairs (user + assistant) until within budget
    while count_tokens(history) > HISTORY_BUDGET and len(history) >= 2:
        history = history[2:]   # remove oldest user + assistant turn
    return history
```

---

## 3. History Growth and Budget Pressure

| Turns | Avg tokens/turn | Cumulative history tokens | Fraction of 8k window |
|-------|----------------|--------------------------|----------------------|
| 5     | 200             | ~1,020                   | 12%                  |
| 10    | 200             | ~2,040                   | 25%                  |
| 20    | 200             | ~4,080                   | 50%                  |
| 40    | 200             | ~8,160                   | 100% — overflow      |
| 10    | 500             | ~5,040                   | 61%                  |
| 20    | 500             | ~10,080                  | 123% — overflow      |

At 200 tokens per turn, a conversation overflows an 8k window at turn 40. At 500 tokens per
turn — typical for responses that include code or structured output — overflow occurs before
turn 20. The budget ceiling must be enforced before it is breached, not after.

---

## 4. Engineering Implications

**The history list is unbounded by default.** Python lists grow indefinitely. An application
that appends to history without a budget check will eventually cause an API error
(`context_length_exceeded`) or silently truncate the prompt on the server side. Budget
enforcement must be built into the accumulation loop, not added as an afterthought.

**Token counting is approximate for open-weight models.** Ollama-served models may use
tokenizers that differ slightly from tiktoken's GPT-4 encoding. A safety margin of
10–15% of the context window absorbs this approximation error reliably.

**The system prompt competes with history for budget.** A 2,000-token system prompt on an
8k-window model leaves only 6,000 tokens for history, output, and retrieved content
combined. System prompt size is a design constraint, not an afterthought.

**Role alternation must be preserved.** The messages API requires `user` and `assistant`
messages to alternate. Dropping an odd number of messages creates a malformed sequence
(two consecutive user messages) that some providers reject. Truncation must always remove
complete pairs.

---

## 5. Implementation Connection

`lab-conversation-history` implements a terminal chat loop with explicit token tracking.
The lab displays the current history token count and budget remaining after each turn,
making the growth curve visible. It also demonstrates what happens when the budget is
exceeded without enforcement — the observable output is either a provider error or a
response that ignores early context.

---

## 6. Failure Modes and Limitations

**Silent context truncation.** Some providers truncate the prompt server-side when the
context window is exceeded, returning a response without signaling that input was dropped.
The model's answer appears coherent but is based on incomplete history. Applications that
rely on early-conversation facts — a user's stated goal, a constraint mentioned at turn 2 —
will produce incorrect behavior silently.

**Off-by-one in token estimation.** Token count formulas are model-specific and
approximate. An undercount by 5% on a heavily loaded context window can cause occasional
API errors. The safety margin exists precisely for this case; removing it to maximize
context space is a common optimization that backfires under variable message lengths.

**Stateless history is session-scoped.** A history list held in application memory is lost
when the process restarts or the session ends. For applications that require cross-session
continuity, the history must be persisted to an external store — the subject of
`external-memory.md`.

---

## 7. Summary

Conversation history is an application-managed list of prior turns injected into every API
call. It grows by two messages per exchange and must be bounded by a token budget calculated
from the context window minus system prompt, output reservation, and safety margin. When the
budget is exceeded, the oldest turns must be dropped in complete pairs. The accumulation
pattern is straightforward; the discipline is in enforcing the ceiling before it is
breached — and in recognizing that in-memory history is session-scoped and must be
externalized for cross-session recall.
