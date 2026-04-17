# Multi-Agent Coordination Patterns

Multi-agent systems decompose a complex task into sub-tasks assigned to specialized agents.
Coordination — deciding which agent runs next, what context it receives, and how results
are aggregated — is the primary engineering challenge. The coordination pattern determines
how context flows, how state is shared, and how failures propagate.

## Orchestrator-Subagent Pattern

An orchestrator agent receives the original task, decomposes it into sub-tasks, delegates
each sub-task to a specialized subagent, and aggregates the results into a final response.

Properties:
- The orchestrator does not execute domain tools directly — it invokes subagents as tools.
- Each subagent operates with its own isolated message accumulator and tool set.
- The subagent receives only the sub-task description — not the orchestrator's full context.
- The subagent returns a summarized result, not its full message history.

Context isolation is the key design constraint: if the orchestrator passes its full context
to every subagent, each subagent call consumes O(n) tokens where n is the orchestrator's
history length. For 5 subagents over 10 orchestrator turns, this is 50× the baseline cost.
Isolation keeps each subagent's input bounded to the sub-task description plus its own history.

## Message Passing

In conversation-based multi-agent systems (AutoGen, CrewAI), agents communicate by
appending messages to a shared transcript. Each message has a sender role and content.
The coordination algorithm (the "speaker selection policy") decides which agent sends the
next message.

Message passing models:
- **Round-robin**: agents take turns in a fixed order. Simple but ignores task state.
- **LLM-based routing**: a moderator LLM reads the transcript and selects the next speaker
  based on the content of the last message. Flexible but non-deterministic.
- **Rule-based routing**: explicit conditions determine the next speaker
  (e.g., "after the Researcher speaks, always invoke the Critic"). Predictable.

The transcript grows linearly with the number of messages. All agents in a shared-transcript
system receive the full history on each invocation — context cost grows with the session.

## State Isolation vs. Shared State

Two coordination models exist for multi-agent state:

**Shared transcript model**: all agents read and write to a single conversation history.
Used by AutoGen GroupChat and LangGraph multi-agent. Simple to implement; expensive
at scale because all agents see all messages.

**Isolated state model**: each agent maintains its own message accumulator. The orchestrator
invokes subagents via function calls, passing only the task input and receiving only the result.
Used by the raw orchestrator-subagent pattern. More expensive to implement; scales to large
agent counts because subagent cost is independent of orchestrator history.

## Failure Propagation

Agent failures propagate differently depending on the coordination topology:

**Sequential pipeline (A → B → C)**: failure in A blocks all downstream agents. The
pipeline must either retry A or accept partial results.

**Parallel fan-out (orchestrator → [A, B, C])**: A's failure does not block B or C.
The orchestrator receives partial results and must decide whether to proceed, retry A,
or report failure.

**Retry policy**: transient failures (LLM API timeout, rate limit) should be retried
with exponential backoff. Permanent failures (invalid tool arguments, missing resource)
should surface as error results rather than blocking the orchestrator.

The orchestrator should always check for error markers in subagent results before
including them in the final response. A subagent that returns an error string should be
noted in the output rather than causing the orchestrator to hallucinate a result.

## ReAct in Multi-Agent Systems

In a multi-agent context, ReAct can be applied at the subagent level without changing the
orchestrator's coordination logic. A ReAct subagent produces a Thought → Action →
Observation cycle visible in its own message accumulator, giving the orchestrator a
traceable log when the subagent result is returned as a tool result summary.

Applying ReAct at the orchestrator level produces a meta-reasoning trace: the orchestrator
reasons about which subagent to invoke next, acts by invoking it, and observes its result
before deciding the next step. This is the plan-and-execute pattern applied to agent
delegation rather than tool dispatch.

## Termination Conditions

Multi-agent conversations need explicit termination conditions. Without them, the
conversation runs until a token or round limit is hit.

Common termination signals:
- **Keyword termination**: a designated string in the last message (e.g., "TASK_COMPLETE").
- **Role-based termination**: a specific agent (e.g., the Critic) approves the output.
- **Round limit**: the session ends after N messages regardless of content.
- **Consensus**: all agents agree on a result (requires a voting mechanism).

Keyword termination is the simplest and most commonly used pattern. Its weakness is
dependence on the model consistently producing the termination keyword — inconsistent
instruction following causes the conversation to overshoot.

## Parallelism

Tasks with independent sub-tasks can be executed in parallel to reduce total latency.
In code:
- Synchronous fan-out: invoke subagents sequentially, collect all results, then aggregate.
  Latency = sum(subagent latencies).
- Asynchronous fan-out: invoke all subagents concurrently with `asyncio.gather()` or a
  thread pool. Latency = max(subagent latencies).

For 5 subagents each taking 3 seconds, synchronous fan-out takes 15 seconds; async takes 3.
The trade-off: async increases peak API concurrency, which may trigger rate limits.
