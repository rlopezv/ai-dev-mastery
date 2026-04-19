---
id: "lab-autogen"
title: "AutoGen — Two-Agent Conversation and GroupChat"
type: "lab-readme"
step: "frameworks-tools"
path: "labs/frameworks-tools/lab-autogen/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "AutoGen"
  - "ConversableAgent"
  - "GroupChat"
  - "agent conversation"
  - "human-in-the-loop"

prerequisites:
  - "docs/frameworks-tools/autogen.md"
  - "docs/ai-agents/multi-agent-systems.md"

related:
  - "docs/frameworks-tools/architecture.md"
  - "docs/frameworks-tools/framework-comparison.md"

summary: "Implements a two-agent AutoGen task completion loop and a three-agent GroupChat demonstrating conversation-based coordination, tool execution via UserProxyAgent, and termination detection."
---

# AutoGen — Two-Agent Conversation and GroupChat

## Navigation

[Labs](../../README.md) / [Frameworks and Tools — Labs](../README.md) / AutoGen — Two-Agent Conversation and GroupChat

---


## Overview

This lab implements two AutoGen conversation patterns:

**Demo 1 — Two-agent conversation.** An `AssistantAgent` backed by an LLM uses a
`search_docs` tool to research a topic. A `UserProxyAgent` executes the tool call and
returns the result. The conversation terminates when the assistant emits "TERMINATE".

**Demo 2 — GroupChat with three agents.** A Researcher, a Critic, and a Writer collaborate
through a shared transcript managed by a `GroupChatManager`. The Researcher searches,
the Critic reviews, and the Writer produces the final answer. The `speaker_selection_method`
determines which agent speaks next.

Out of scope: code execution (`code_execution_config` is disabled for safety), human input
mode (`ALWAYS`/`TERMINATE`), and AutoGen Studio.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `ConversableAgent` | `main.py` — `AssistantAgent` and `UserProxyAgent` are both `ConversableAgent` subclasses |
| `agent conversation` | `main.py:demo_two_agent()` — `user_proxy.initiate_chat(assistant, ...)` drives the loop |
| `ConversableAgent` (tool dispatch) | `main.py` — `function_map={"search_docs": search_docs}` routes tool calls to `UserProxyAgent` |
| `GroupChat` | `main.py:demo_group_chat()` — `GroupChat(agents=[...])` + `GroupChatManager` |
| `human-in-the-loop` | `main.py` — `human_input_mode="NEVER"` disables it; change to `"ALWAYS"` to enable |

---

## Setup

```bash
# AutoGen requires OpenAI API — Ollama is not supported by this lab
# Set your API key
export OPENAI_API_KEY=sk-...

# Install dependencies
pip install -r labs/frameworks-tools/requirements.txt
```

---

## Run

```bash
cd labs/frameworks-tools/lab-autogen
python main.py
```

Environment variable overrides:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required — OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model used by all agents |

---

## Expected Output

```
============ DEMO 1 — Two-agent conversation ============
Task: Search for information about HNSW and explain how it achieves fast retrieval.

user_proxy (to assistant):
Search for information about HNSW and explain how it achieves fast retrieval.

assistant (to user_proxy):
***** Suggested function call: search_docs *****
Arguments:
{"query": "hnsw approximate nearest neighbor search"}
***** Suggested function call: search_docs *****

user_proxy (to assistant):
***** Response from calling function "search_docs" *****
HNSW (Hierarchical Navigable Small World) builds a multi-layer graph for
approximate nearest-neighbor search...
*****

assistant (to user_proxy):
HNSW achieves fast retrieval by building a hierarchical graph with long-range
connections at the top layer and progressively shorter connections below.
Queries greedy-walk from the coarse top layer down to fine layers, finding the
approximate nearest neighbor without exhaustive comparison. TERMINATE

user_proxy (to assistant):
```

```
============ DEMO 2 — GroupChat with three agents ============
Task: Research how LLM API rate limiting works...

--- GroupChat conversation ---
Researcher (to chat_manager):
***** Suggested function call: search_docs *****
Arguments: {"query": "rate limiting llm api"}
...
Critic (to chat_manager):
The summary accurately covers RPM/TPM limits and exponential backoff. APPROVED.

Writer (to chat_manager):
LLM APIs enforce requests-per-minute (RPM) and tokens-per-minute (TPM) limits,
returning HTTP 429 when exceeded. The recommended mitigation is exponential backoff
with jitter: delay = min(base × 2^attempt + jitter, max_delay), respecting the
Retry-After header and never retrying non-429 4xx errors. TERMINATE
```

---

## What to observe

- **Termination detection in Demo 1**: watch for the final assistant message ending with
  "TERMINATE". The `is_termination_msg` lambda returns `True` for this message and the
  loop exits cleanly. Compare with what happens in the failure case — the conversation
  runs until the ceiling fires.

- **Tool execution path in Demo 1**: the assistant emits a function call; the
  `UserProxyAgent` dispatches it via `function_map` and returns the result as the next
  message. The assistant receives the tool result and produces its final answer.
  No orchestration code — the conversation structure drives the flow.

- **Speaker selection in Demo 2**: after each message, the `GroupChatManager` selects
  the next speaker. With `speaker_selection_method="auto"`, it uses an LLM call to decide.
  Notice the order: Researcher → Critic → (possible re-research) → Writer. The pattern
  emerges from agent system messages and the transcript, not from explicit rules.

- **Full transcript as shared state**: every agent in Demo 2 receives the full conversation
  history. As the GroupChat grows, each agent call's input token count grows with it.
  For 4 rounds × 3 agents, every agent reads ~12 prior messages on the last round.

---

## Concepts verified

- [ ] `ConversableAgent` — observable as both `AssistantAgent` and `UserProxyAgent` sending and receiving messages
- [ ] `agent conversation` — observable as the conversation loop driven by `initiate_chat` without explicit orchestration code
- [ ] `ConversableAgent` (tool dispatch) — observable as `***** Response from calling function *****` in the transcript
- [ ] `GroupChat` — observable as three named agents each contributing messages in Demo 2
- [ ] Termination — observable as the conversation ending after "TERMINATE" without hitting `max_consecutive_auto_reply`

---

## Failure case

Active experiment: modify `main.py` at the marked `# FAILURE CASE` block and re-run.

- **What to change:** in `demo_two_agent()`, remove the TERMINATE instruction from
  the assistant's `system_message`. Change:
  ```python
  "...When the task is complete, end your response with the word TERMINATE."
  ```
  to:
  ```python
  "...When the task is complete, provide your final answer."
  ```
- **Expected degradation:**
  - The conversation does not terminate naturally — the assistant never emits "TERMINATE"
  - The loop runs until `max_consecutive_auto_reply` is exhausted (10 turns)
  - The final message is from the system: maximum consecutive replies reached
  - This demonstrates that the termination condition must be explicit in the system prompt

Restore the original system message after the experiment.

---

## Infrastructure

| Service | Purpose |
|---------|---------|
| OpenAI API | Required — provides the LLM for all agents; Ollama is not supported by AutoGen's function-calling interface |
