---
id: "memory-context-validation"
title: "Memory and Context Management — Validation"
type: "validation"
step: "memory-context"
path: "docs/memory-context/validation.md"
status: "draft"
level: "intermediate"

concepts:
  - "memory types"
  - "conversation history"
  - "context management"
  - "external memory"
  - "token budget"

prerequisites:
  - "docs/memory-context/implementation-reference.md"

next:
  - "docs/ai-agents/README.md"

related:
  - "docs/memory-context/README.md"
  - "docs/memory-context/architecture.md"

implementation_refs:
  - "labs/memory-context/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines the conceptual, practical, and lab-level criteria for completing the memory-context module."
---

# Memory and Context Management — Validation

## Navigation

[Docs](../README.md) / [Memory and Context Management](README.md) / Memory and Context Management — Validation

---

## 1. Validation Overview

This module is complete when the learner can distinguish the four memory mechanisms by
their storage, lifetime, and retrieval properties; implement a token-bounded conversation
history with at least two context management strategies; and build a cross-session memory
system that writes, retrieves, and injects external memory entries.

Expected mastery level: **intermediate** — the learner can implement a production-ready
memory layer for a multi-turn LLM application.

---

## 2. Conceptual Validation

| Concept | Validation Method |
|---------|------------------|
| Memory types | Explain the difference between in-context, episodic, semantic, and parametric memory without reference materials. Identify which type is appropriate for a given use case. |
| Token budget | Calculate the available history budget given context window size, system prompt size, and output reservation. Identify when a 20-turn conversation at 300 tokens/turn will overflow a 8k context window. |
| Sliding window | Describe what information is lost when a sliding window of 10 turns is applied to a 25-turn conversation and why this may or may not matter. |
| Summarization compression | Explain why summarization preserves early context better than truncation and what the cost is (latency, additional API call). |
| External memory lifecycle | Trace a memory entry from the moment a fact is stated by the user, through embedding and storage, to retrieval and injection in a future session. |

---

## 3. Practical Validation

```text
Task 1: Token-bounded history
Build a conversation loop that:
- Accumulates history across turns
- Counts tokens after each append
- Enforces a budget ceiling before each API call
- Never sends a request that exceeds the context window
Expected: No API errors after 50+ turns; early messages are dropped when budget is reached.

Task 2: Summarization strategy
Extend Task 1 to trigger summarization when token count exceeds 80% of budget.
Expected: Older turns are replaced by a one-paragraph summary; the model can answer
questions about early-conversation facts after compression.

Task 3: Cross-session recall
Run two separate sessions with the same user identifier.
In session 1: state a fact (e.g., "I prefer concise answers").
In session 2: ask a question and verify the fact is recalled without being restated.
Expected: Retrieved memory entry is injected; response reflects the stated preference.
```

---

## 4. Lab Validation

| Lab | Validation Criteria |
|-----|---------------------|
| `lab-memory-types` | In-context and external memory produce observably different behavior when queried about a fact established in turn 1 after 20+ turns |
| `lab-conversation-history` | Token count is displayed per turn; budget ceiling enforced; no API errors across 50-turn run |
| `lab-context-management` | All three strategies (truncation, sliding window, summarization) run without error; summarization demonstrates higher early-context recall accuracy than truncation |
| `lab-external-memory` | Episode written in session 1 is retrieved and injected in session 2; semantic fact updated via upsert propagates to retrieval |
| `lab-integration` | Full system runs 30+ turns without budget violation; cross-session recall works; memory write executes asynchronously |

---

## 5. Integration Validation

The learner should be able to explain:

- Why the context assembler must allocate tokens in priority order (system prompt → memory → history → user message) rather than concatenating all sources without a ceiling
- Why a sliding window that keeps the last 10 turns provides different guarantees than a token budget that keeps the last 2,000 tokens
- Why external memory and in-context history are complementary rather than alternatives — and in what scenario you would use both simultaneously
- Why the memory writer runs after the response is returned rather than before the model is called

---

## 6. Failure Detection

**Confusion between memory type and memory location.** A common error is treating
"in-context" as a type of memory distinct from conversation history rather than recognizing
that conversation history IS in-context memory. If the learner cannot place history
accumulation within the in-context memory category, revisit `memory-types.md`.

**Token budget miscalculation.** If the learner sets the budget at the context window size
rather than at context window minus system prompt, output reservation, and safety margin,
the application will overflow on every long conversation. Revisit `conversation-history.md`
section 2.2 on budget ceiling.

**Treating retrieval as guaranteed.** If the learner assumes that stored memory is always
retrieved when relevant, they will not implement relevance threshold filtering or cold-start
handling. Revisit `external-memory.md` section 6 (failure modes).

**Missing role alternation after compression.** Dropping an odd number of messages during
truncation creates two consecutive user messages, causing API errors. If this error appears
in `lab-context-management`, check that truncation always removes complete turn pairs
(user + assistant).

---

## 7. Completion Criteria

This module is complete when:

- All four memory types can be defined and placed in a use-case selection table without reference
- `lab-conversation-history` runs 50 turns without exceeding the context window budget
- `lab-context-management` demonstrates measurably higher early-context recall with summarization than with truncation
- `lab-external-memory` successfully writes and retrieves an episode across two separate process invocations
- `lab-integration` assembles all components into a working multi-turn application with cross-session recall

---

## 8. Self-Assessment Checklist

```text
- [ ] I can explain the difference between episodic and semantic external memory
- [ ] I can calculate a history token budget from context window and prompt parameters
- [ ] I understand why role alternation must be preserved during history truncation
- [ ] I can implement a sliding window strategy that drops complete turn pairs
- [ ] I can implement a summarization trigger at 80% of the history budget
- [ ] I understand what "cold start" means for an external memory store
- [ ] I can trace a memory entry through write → embed → store → retrieve → inject
- [ ] I have run all required labs and observed the expected outputs
```

---

## 9. Next Steps

If validation passes, proceed to `docs/ai-agents/README.md`. The agents module builds
on this module's memory model, extending it with planning state, tool-use history, and
multi-agent coordination.

If validation fails on conceptual questions about memory types, re-read
`docs/memory-context/memory-types.md` before retrying labs.

If validation fails on budget enforcement, re-read `docs/memory-context/conversation-history.md`
section 2.2 and review the `count_tokens()` implementation in `labs/memory-context/shared/config.py`.

If validation fails on cross-session recall, verify that ChromaDB is running with the
`full` profile and that the persistent client is used in `lab-external-memory`.
