---
id: "frameworks-tools-autogen"
title: "AutoGen"
type: "topic"
step: "frameworks-tools"
path: "docs/frameworks-tools/autogen.md"
status: "draft"
level: "intermediate"

concepts:
  - "AutoGen"
  - "ConversableAgent"
  - "GroupChat"
  - "human-in-the-loop"
  - "agent conversation"

prerequisites:
  - "docs/ai-agents/multi-agent-systems.md"
  - "docs/frameworks-tools/langchain.md"

next:
  - "docs/frameworks-tools/semantic-kernel.md"

related:
  - "docs/ai-agents/agent-patterns.md"
  - "docs/frameworks-tools/framework-comparison.md"

implementation_refs:
  - "labs/frameworks-tools/lab-autogen"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how AutoGen models multi-agent coordination as structured conversation between ConversableAgents and when this abstraction fits production requirements."
---

# AutoGen

## Navigation

[Docs](../README.md) / [Frameworks and Tools](README.md) / AutoGen

---

## 1. Intuition

AutoGen makes multi-agent coordination look like a group chat. Instead of writing explicit
orchestration code that decides which agent runs next and what context it receives,
AutoGen models coordination as message exchange: agents send messages to each other, and
each agent decides — based on its configuration and the messages it receives — whether to
respond, call a tool, or defer to a human.

The central insight is that the conversation transcript itself is the shared state. Every
agent in the conversation has access to the full message history, so no explicit state
handoff is needed. The coordination policy emerges from the agents' individual response
functions rather than from a central orchestration loop.

---

## 2. Explanation

### 2.1 Why

Manual multi-agent orchestration requires the developer to implement every coordination
concern: which agent runs next, what context it receives, how tool results propagate, where
human input is injected, and when the conversation terminates. This is manageable for
two-agent pipelines but grows complex as the number of agents and tool-call patterns
increases.

AutoGen was designed to reduce this orchestration burden by treating agents as conversation
participants. The framework handles message routing, role assignment, tool execution, and
termination detection — the developer configures roles and capabilities, not control flow.

### 2.2 How

**ConversableAgent** is the core primitive. Every participant in an AutoGen conversation —
model-backed agents, tool-execution agents, and human proxy agents — is a
`ConversableAgent`. Each agent is configured with:

- `system_message`: the role prompt that shapes the agent's behavior
- `llm_config`: the model and tool definitions the agent can invoke
- `human_input_mode`: whether to request human input (`ALWAYS`, `NEVER`, `TERMINATE`)
- `code_execution_config`: whether to execute code blocks in responses

**Two-agent conversations** are the simplest pattern. A `UserProxyAgent` (representing the
human or the application) initiates a task by calling `initiate_chat` with an
`AssistantAgent`. The agents alternate messages until a termination condition is met —
typically the assistant's reply contains the word "TERMINATE" or the proxy receives a
final answer without further tool calls.

**GroupChat** extends the pattern to three or more agents. A `GroupChatManager` moderates
the conversation: it selects the next speaker based on a configurable strategy (round-
robin, random, or LLM-based routing), passes the full transcript to the selected agent,
and continues until a termination condition is met.

**Tool execution** is delegated to the `UserProxyAgent` by default. When an
`AssistantAgent` emits a tool call or code block, the proxy executes it and sends the
result back as the next message. This keeps execution separate from reasoning — the
assistant reasons, the proxy acts.

### 2.3 Code example

```python
# See: labs/frameworks-tools/lab-autogen/main.py
import autogen

llm_config = {"model": "gpt-4o-mini", "api_key": "..."}

assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="You are a helpful coding assistant.",
    llm_config=llm_config,
)
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "workspace"},
)

user_proxy.initiate_chat(assistant, message="Write a Python function to reverse a string.")
```

---

## 3. Table

| Component | Role | Key configuration |
|-----------|------|-------------------|
| `AssistantAgent` | LLM-backed reasoning agent | `system_message`, `llm_config` |
| `UserProxyAgent` | Task initiator and tool executor | `human_input_mode`, `code_execution_config` |
| `GroupChatManager` | Moderates multi-agent conversations | speaker selection strategy |
| `GroupChat` | Container for group conversation participants | agents list, max rounds |
| `llm_config` | Model and tool definitions | model name, functions/tools list |
| Termination condition | Stops the conversation | keyword match, max turns, custom function |

---

## 4. Engineering Implications

**Full transcript as shared context has cost implications.** Every agent in a GroupChat
receives the full conversation history. As the conversation grows, each model call's input
token count grows with it. For long multi-agent tasks, this leads to rapidly escalating
API costs. Limit `max_round` and design tasks to complete in few turns.

**Code execution creates a side-effect boundary.** When `code_execution_config` is enabled,
AutoGen executes Python code blocks from agent responses in a subprocess. This is powerful
for agentic coding assistants but creates a security boundary: untrusted models can
generate and execute arbitrary code. Use Docker-based execution (`use_docker: True`) in
any production environment.

**Human-in-the-loop integration is explicit.** Setting `human_input_mode="ALWAYS"` pauses
the conversation after every agent response and waits for human input. This makes AutoGen
suitable for workflows where a human must approve intermediate steps, but it requires the
host application to implement the input collection mechanism.

**GroupChat speaker selection is non-deterministic with LLM-based routing.** When the
`GroupChatManager` uses an LLM to select the next speaker, the selection depends on the
model's interpretation of the transcript, which varies between runs. For reproducible
orchestration, use round-robin or explicit rule-based selection.

---

## 5. Implementation Connection

`lab-autogen` implements a two-agent task completion loop and a three-agent GroupChat with
distinct specialist roles. Key observations:

- How `initiate_chat` drives the conversation loop and returns when a termination condition is met
- How tool definitions in `llm_config` are presented to the model and how results flow
  back through the `UserProxyAgent`
- How `GroupChatManager` selects the next speaker and passes the transcript to it

Run the lab with `human_input_mode="NEVER"` first to observe the automated flow, then with
`"TERMINATE"` to see how the stopping condition is detected.

---

## 6. Failure Modes and Limitations

**Termination condition failure.** If the termination condition is too strict (exact string
match) or the model rarely emits the expected signal, conversations run until
`max_round` is exhausted without producing a useful result. Define the termination
condition in the system prompt explicitly and test with multiple queries.

**Context window overflow in long GroupChats.** With four or more agents and many rounds,
the transcript fed to each agent grows beyond the context window of weaker models.
The framework does not truncate automatically. Use summary agents or limit round count.

**Tight coupling to OpenAI-compatible APIs.** AutoGen's `llm_config` is designed around
OpenAI's function-calling format. Using non-OpenAI models requires adapter configuration
and may not support all tool-call patterns.

---

## 7. Summary

AutoGen models multi-agent coordination as structured conversation between
`ConversableAgent` instances. The conversation transcript is the shared state, so no
explicit state handoff is needed between agents — each agent reads the full history and
decides whether and how to respond. This abstraction simplifies coordination logic for
two-agent and small GroupChat scenarios at the cost of growing context windows and
non-deterministic speaker selection in larger groups.
