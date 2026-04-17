---
id: "frameworks-tools-framework-comparison"
title: "Framework Comparison"
type: "topic"
step: "frameworks-tools"
path: "docs/frameworks-tools/framework-comparison.md"
status: "draft"
level: "intermediate"

concepts:
  - "framework selection"
  - "framework abstraction"
  - "framework trade-offs"

prerequisites:
  - "docs/frameworks-tools/langchain.md"
  - "docs/frameworks-tools/llamaindex.md"
  - "docs/frameworks-tools/autogen.md"
  - "docs/frameworks-tools/semantic-kernel.md"

next:
  - "docs/frameworks-tools/architecture.md"

related:
  - "docs/ai-agents/agent-patterns.md"
  - "docs/rag/architecture.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Provides structured selection criteria for choosing between LangChain, LlamaIndex, AutoGen, and Semantic Kernel based on use case, team context, and operational requirements."
---

## 1. Intuition

Selecting an AI framework is not a question of which one is best — it is a question of fit
between the framework's primary abstraction and the dominant concern of the application.
LangChain is a general-purpose orchestration framework. LlamaIndex is a data and retrieval
framework. AutoGen is a multi-agent conversation framework. Semantic Kernel is an
enterprise integration framework. Each excels at its primary use case and incurs overhead
when used outside it.

The instinct to "pick one framework and use it for everything" leads to architectures where
the framework fights the use case. The better instinct is to match the abstraction to the
problem — and to know when no framework is the right choice.

---

## 2. Explanation

### 2.1 Why

Every framework encodes a set of assumptions about how AI applications should be
structured. Those assumptions are expressed through the abstractions the framework provides
and the patterns it incentivizes. When your application fits those assumptions, the
framework accelerates development. When your application does not, the framework adds
complexity without value.

The cost of the wrong framework is not just wasted effort at the time of selection. It
is the ongoing cost of working around abstractions that do not fit, debugging behavior that
is obscured by framework internals, and onboarding engineers who must understand both the
application domain and the framework's internal model.

### 2.2 How

The primary question is: what is the dominant engineering concern?

**If the concern is composing multi-step LLM pipelines** with prompt chaining, memory, and
tool routing, LangChain is the natural fit. LCEL makes the pipeline structure explicit and
composable. The ecosystem provides ready-made integrations for most LLM providers,
vector stores, and tool types.

**If the concern is connecting LLMs to large, heterogeneous document corpora**, LlamaIndex
is the natural fit. Its indexing, retrieval, and synthesis abstractions are optimized for
this problem. Using LangChain for a complex RAG pipeline is possible but requires
re-implementing much of what LlamaIndex provides.

**If the concern is multi-agent coordination** where agents collaborate on tasks through
structured conversation, AutoGen is the natural fit. Its conversation abstraction reduces
orchestration code, and its human-in-the-loop support is first-class.

**If the concern is integrating AI capabilities into an existing enterprise application**
with multiple service integrations, versioned prompts, and .NET compatibility requirements,
Semantic Kernel is the natural fit. Its plugin and planner model maps well to
service-oriented architectures.

**If the pipeline is a single LLM call with a fixed prompt**, no framework is the right
choice. The overhead of any framework is unwarranted.

### 2.3 Code example

```python
# No code example for this topic — framework selection is a design decision, not a coding pattern.
# See the individual framework topics for implementation references.
```

---

## 3. Table

| Dimension | LangChain | LlamaIndex | AutoGen | Semantic Kernel |
|-----------|-----------|------------|---------|-----------------|
| **Primary abstraction** | Runnable chain | Index + query engine | ConversableAgent | Kernel + plugin |
| **Primary use case** | Multi-step orchestration | Retrieval pipelines | Multi-agent conversation | Enterprise integration |
| **RAG support** | Via retriever components | Native, optimized | Limited | Via memory plugins |
| **Agent support** | Via AgentExecutor | Basic | Native, multi-agent | Via planner |
| **Memory support** | Via MessageHistory | Via storage context | Via transcript | Via memory store |
| **Language** | Python, JS/TS | Python | Python | Python, C# |
| **Enterprise / .NET** | No | No | No | Yes |
| **Abstraction depth** | High | Medium | Medium | High |
| **Debugging difficulty** | High | Medium | Medium | Medium |
| **Ecosystem maturity** | High | High | Medium | Medium |

---

## 4. Engineering Implications

**Frameworks are hard to replace mid-project.** Once a retrieval pipeline is built on
LlamaIndex's index abstraction, replacing it with a raw vector store requires rewriting
not just the retrieval code but all the metadata, persistence, and query configuration
that accumulated on the index. Choose early and commit — or design the abstraction
boundary so the framework is replaceable.

**Mixing frameworks is a valid pattern.** It is common to use LlamaIndex for indexing and
retrieval and LangChain for the chain that wraps the query engine. Both frameworks expose
standard interfaces that compose without tight coupling. The cost is having two framework
dependency trees and two debugging surfaces.

**No-framework is a legitimate option.** For applications with a single, stable pipeline
and a small engineering team, raw API calls with a few helper functions may be more
maintainable than a framework with its own abstractions, versioning, and behavior.
The decision threshold: if you are implementing retrieval, multi-step chaining, multi-agent
coordination, or tool routing, a framework pays off. If you are making one LLM call per
request, it does not.

**Framework updates are breaking changes.** All four frameworks release breaking API
changes in minor versions. Pin versions in `requirements.txt` and treat framework upgrades
as planned migration tasks, not routine dependency updates.

---

## 5. Implementation Connection

This is a concept-only topic. There is no lab for framework comparison. The decision
criteria in this document apply when choosing a starting framework for each lab in the
module. Review the labs README and run `lab-langchain` and `lab-llamaindex` to develop
hands-on intuition before applying the selection criteria to production decisions.

---

## 6. Failure Modes and Limitations

**Selecting a framework for its name recognition.** LangChain has high awareness due to
community activity, not necessarily because it is the right fit for every problem.
Evaluate frameworks against use case requirements, not popularity metrics.

**Abstracting too early.** Adding a framework abstraction before the pipeline is fully
understood traps design decisions in the framework's model. Build the pipeline as raw
API calls first, identify the recurring patterns, then introduce the framework where those
patterns appear.

**Underestimating debugging cost.** Framework abstractions hide intermediate values.
Debugging a five-step LCEL chain requires tracing through the Runnable protocol. Debugging
a LlamaIndex query engine requires understanding the Node metadata model. Budget time for
framework-specific debugging, not just application logic debugging.

---

## 7. Summary

Framework selection is a design decision driven by use case fit. LangChain for
orchestration, LlamaIndex for retrieval, AutoGen for multi-agent conversation, Semantic
Kernel for enterprise integration. Mixing frameworks at well-defined interfaces is a valid
architecture. No framework is the right choice for simple single-call pipelines. All
frameworks introduce debugging surface and version management overhead — account for both
in the architectural decision.
