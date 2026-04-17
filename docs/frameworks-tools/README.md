---
id: "frameworks-tools-readme"
title: "Frameworks and Tools"
type: "step-readme"
step: "frameworks-tools"
path: "docs/frameworks-tools/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain"
  - "LlamaIndex"
  - "AutoGen"
  - "Semantic Kernel"
  - "framework abstraction"
  - "framework selection"

prerequisites:
  - "ai-agents"

next:
  - "docs/frameworks-tools/langchain.md"

related:
  - "docs/ai-agents/README.md"
  - "docs/rag/README.md"
  - "docs/memory-context/README.md"

implementation_refs:
  - "labs/frameworks-tools/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Introduces the major Python AI frameworks — LangChain, LlamaIndex, AutoGen, and Semantic Kernel — and explains when and why to use each one."
---

## 1. Overview

Building AI applications from raw API calls is possible but repetitive. Every project
reimplements the same patterns: chaining prompts, managing retrieval pipelines, routing
tool calls, coordinating multiple agents. Frameworks exist to codify these patterns into
reusable abstractions so engineers can compose capabilities instead of re-engineering them.

This module examines four frameworks that cover distinct segments of the AI engineering
landscape: LangChain for orchestration and chaining, LlamaIndex for data-intensive retrieval
pipelines, AutoGen for multi-agent conversation systems, and Semantic Kernel for enterprise
.NET and Python AI integration. Each framework makes different trade-offs between
expressiveness, composability, and operational overhead.

The capability this module unlocks is selecting and applying the right framework for a
given system requirement — and knowing when to build without one.

---

## 2. Scope

**Covered:**
- LangChain: chains, memory, agents, tools, and LCEL (LangChain Expression Language)
- LlamaIndex: indexing pipelines, query engines, node parsers, and retrieval
- AutoGen: multi-agent conversation patterns and agent roles
- Semantic Kernel: kernel, plugins, planners, and enterprise integration
- Framework comparison: decision criteria for selecting a framework
- Integration architecture: how frameworks connect to underlying APIs and infrastructure

**Not covered:**
- LangGraph (graph-based agentic flows — an extension of LangChain beyond this module scope)
- Fine-tuning or custom model training
- Production deployment and scaling of framework-based applications (covered in `deployment-scaling`)
- Evaluation and testing of framework pipelines (covered in `evaluation-testing`)

---

## 3. Key Concepts

**LangChain** — a Python and JavaScript framework for composing LLM-powered applications
through a declarative chain interface (LCEL), with built-in support for memory, retrieval,
tool use, and agents.

**LlamaIndex** — a data framework for connecting LLMs to external data sources through
structured indexing and query pipelines, optimized for retrieval-augmented generation at
production scale.

**AutoGen** — a Microsoft framework for building multi-agent systems through a conversation
abstraction, where agents exchange messages and coordinate to complete tasks without manual
orchestration code.

**Semantic Kernel** — a Microsoft SDK for integrating AI capabilities into enterprise
applications, built around a kernel that routes task execution across plugins, memory
stores, and planners.

**framework abstraction** — the mechanism by which a framework wraps raw API calls into
higher-level constructs (chains, nodes, agents, plugins) that encode recurring patterns and
manage state transitions.

**framework selection** — the decision process for choosing a framework based on use case
fit, operational overhead, team familiarity, and the cost of abstractions that cannot be
bypassed when they behave unexpectedly.

---

## 4. Concept Map

```text
                    ┌─────────────────────────────────────┐
                    │         AI Application Needs         │
                    └──────────────┬──────────────────────┘
                                   │
          ┌────────────────────────┼──────────────────────────┐
          ▼                        ▼                           ▼
 ┌─────────────────┐    ┌──────────────────────┐    ┌────────────────────┐
 │   Orchestration  │    │  Retrieval Pipelines  │    │  Multi-Agent Coord │
 │   + Chaining     │    │  + Data Indexing      │    │  + Conversation    │
 │                  │    │                        │    │                    │
 │   LangChain      │    │   LlamaIndex           │    │   AutoGen          │
 │   (LCEL)         │    │   (Query Engines)      │    │   (ConversableAgent│
 └─────────────────┘    └──────────────────────┘    └────────────────────┘
          │                        │                           │
          └────────────────────────┼──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │   Enterprise Integration              │
                    │   Semantic Kernel (Plugins/Planners) │
                    └─────────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │   Framework Comparison                │
                    │   (selection criteria)               │
                    └─────────────────────────────────────┘
```

---

## 5. Learning Flow

```text
langchain.md             → LCEL chains, memory, and agents in LangChain
llamaindex.md            → Indexing, nodes, query engines, and retrieval
autogen.md               → Multi-agent conversation with AutoGen
semantic-kernel.md       → Kernel, plugins, planners for enterprise integration
framework-comparison.md  → When to use which framework — selection criteria
workflow-tools.md        → Visual and low-code AI workflow tools — awareness and limits
architecture.md          → How framework components compose at system level
implementation-reference.md → Patterns and design decisions across the labs
validation.md            → Completion criteria and self-assessment
```

`langchain.md` and `llamaindex.md` are the required core topics. `autogen.md` and
`semantic-kernel.md` are optional — read them to understand the framework landscape before
choosing one for production work. `framework-comparison.md` is best read after all four
framework topics.

---

## 6. Documentation Structure

```text
docs/frameworks-tools/
├── README.md                    ← this file
├── langchain.md                 ← topic: LangChain orchestration and LCEL
├── llamaindex.md                ← topic: LlamaIndex retrieval and indexing
├── autogen.md                   ← topic: AutoGen multi-agent conversations
├── semantic-kernel.md           ← topic: Semantic Kernel enterprise integration
├── framework-comparison.md      ← topic: selection criteria and trade-offs
├── workflow-tools.md            ← topic: visual and low-code AI workflow tools (concept-only)
├── architecture.md              ← system architecture
├── implementation-reference.md  ← implementation patterns
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

| Lab | Type | Purpose |
|-----|------|---------|
| `lab-langchain` | implementation | Build a LangChain pipeline with LCEL, memory, and tool routing |
| `lab-llamaindex` | implementation | Build a LlamaIndex retrieval pipeline over a document corpus |
| `lab-autogen` | implementation | Implement a multi-agent conversation with AutoGen |
| `lab-semantic-kernel` | implementation | Build a kernel-based application with plugins and a planner |
| `lab-integration` | module-integration | Compose framework components into a full application |

`lab-langchain` and `lab-llamaindex` are required. `lab-autogen`, `lab-semantic-kernel`,
and `lab-integration` are optional.

---

## 8. How to Use This Module

Read `langchain.md` first — it establishes the chain abstraction that the other frameworks
build on in different ways. Then read `llamaindex.md` to understand the retrieval-focused
design. After those two, you can read `autogen.md`, `semantic-kernel.md`, and
`framework-comparison.md` in any order.

Run `lab-langchain` and `lab-llamaindex` after their respective topics. These two labs are
required. The optional labs extend the picture for teams considering AutoGen or Semantic
Kernel in production.

The module uses a shared `corpus/` folder — read the labs README before running individual
labs.

---

## 9. Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `ai-agents` | LangChain and AutoGen implement agent abstractions over the agent loop covered in this module |
| `rag` | LlamaIndex provides a framework-level RAG pipeline over the concepts introduced there |
| `memory-context` | LangChain and LlamaIndex both wrap conversation history and external memory patterns from this module |
| `evaluation-testing` | Framework pipelines are evaluated using techniques from this module |

---

## 10. Next Steps

Begin with `docs/frameworks-tools/langchain.md` to understand how LangChain's chain
abstraction and LCEL compose LLM operations before examining data-centric or multi-agent
frameworks.
