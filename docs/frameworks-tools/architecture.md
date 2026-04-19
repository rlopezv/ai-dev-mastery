---
id: "frameworks-tools-architecture"
title: "Frameworks and Tools — Architecture"
type: "architecture"
step: "frameworks-tools"
path: "docs/frameworks-tools/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "framework abstraction"
  - "LangChain"
  - "LlamaIndex"
  - "AutoGen"
  - "Semantic Kernel"
  - "pipeline composition"

prerequisites:
  - "docs/frameworks-tools/README.md"
  - "docs/frameworks-tools/langchain.md"
  - "docs/frameworks-tools/llamaindex.md"

next:
  - "docs/frameworks-tools/implementation-reference.md"

related:
  - "docs/frameworks-tools/autogen.md"
  - "docs/frameworks-tools/semantic-kernel.md"
  - "docs/frameworks-tools/framework-comparison.md"
  - "docs/ai-agents/architecture.md"

implementation_refs:
  - "labs/frameworks-tools/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes how AI framework components compose at system level — from raw API calls through framework abstractions to a complete application pipeline."
---

# Frameworks and Tools — Architecture

## Navigation

[Docs](../README.md) / [Frameworks and Tools](README.md) / Frameworks and Tools — Architecture

---

## 1. System Overview

An AI application built with frameworks sits on three layers. The bottom layer is the
infrastructure: LLM APIs, embedding models, vector stores, and external tools. The middle
layer is the framework: abstract components that wrap infrastructure calls and enforce a
composition model. The top layer is the application: domain logic that assembles framework
components into a pipeline that solves a specific problem.

The architecture question is where to draw the boundaries between layers — specifically,
how much of the application logic to express through framework abstractions and how much
to implement as raw code outside the framework.

This document describes a reference integration architecture that uses LangChain for
orchestration and LlamaIndex for retrieval, connected to a shared infrastructure layer,
and shows how AutoGen and Semantic Kernel occupy the same layer for different use cases.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| LLM API (OpenAI, Anthropic, Ollama) | LLM execution | Generates text from input messages |
| Embedding model | Vector representation | Converts text to embedding vectors for retrieval |
| Vector store (ChromaDB, Pinecone) | Retrieval backend | Stores and queries embeddings at scale |
| LangChain LCEL chain | Pipeline orchestration | Connects prompt, model, parser, retriever |
| LangChain AgentExecutor | Agent loop | Runs tool-use loop with stop condition |
| LlamaIndex VectorStoreIndex | Document retrieval | Indexes nodes and retrieves by similarity |
| LlamaIndex QueryEngine | Retrieval pipeline | End-to-end retrieval and response synthesis |
| AutoGen ConversableAgent | Agent participant | Reasons, invokes tools, emits responses |
| Semantic Kernel Kernel | AI service registry | Routes invocations to registered plugins |
| Corpus | Document source | Fixed set of source documents for retrieval labs |

---

## 3. Component Interactions

**LangChain orchestration layer** connects to the LLM API via a model wrapper
(`ChatOpenAI`, `ChatAnthropic`). It connects to a retrieval backend via a `Retriever`
that wraps either a LlamaIndex query engine or a raw vector store. Memory is injected
as a `MessageHistory` wrapper around the chain.

**LlamaIndex retrieval layer** is independent of the orchestration layer. It connects
to the embedding model for index construction and to the vector store for persistence.
The query engine returns nodes with metadata that the LangChain chain injects into
its prompt template.

**AutoGen** replaces the LangChain orchestration layer when multi-agent conversation is
the primary pattern. Agents connect to the LLM API directly via `llm_config`. Tool
execution is handled by the `UserProxyAgent` and does not require a separate framework
component.

**Semantic Kernel** replaces both the orchestration and memory layers for enterprise
scenarios. The kernel connects to the LLM API via a registered AI service, and to the
memory store via a registered memory service. All function invocations, including tool
calls, are routed through the kernel.

---

## 4. Data Flow (MANDATORY)

### LangChain + LlamaIndex pipeline

```text
User query
  │
  ▼
LangChain LCEL chain
  │
  ├─→ LlamaIndex QueryEngine
  │       │
  │       ├─→ VectorStoreIndex (ChromaDB)
  │       │       │
  │       │       └─→ Embedding model → similarity search → top-k Nodes
  │       │
  │       └─→ ResponseSynthesizer → assembled context
  │
  ├─→ ChatPromptTemplate (query + retrieved context)
  │
  ├─→ LLM API (OpenAI / Anthropic / Ollama)
  │
  └─→ StrOutputParser → string response → application
```

### AutoGen multi-agent flow

```text
UserProxyAgent.initiate_chat(message)
  │
  ▼
AssistantAgent (LLM call) → response with tool call
  │
  ▼
UserProxyAgent (tool execution) → tool result message
  │
  ▼
AssistantAgent (LLM call with result) → final answer or next tool call
  │
  ▼
Termination condition met → conversation ends
```

### Semantic Kernel planner flow

```text
kernel.invoke_prompt(task)
  │
  ▼
FunctionChoiceBehavior planner → tool list presented to LLM
  │
  ▼
LLM selects plugin function → kernel dispatches to plugin
  │
  ▼
Plugin returns result → kernel feeds result back to LLM
  │
  ▼
LLM emits final response → application
```

---

## 5. Execution Flow

**LCEL chain execution** is synchronous and lazy. The chain is defined declaratively with
`|` and executed when `invoke` is called. Each `Runnable` in the chain receives the output
of the previous one. Streaming propagates automatically if all components support it.

**LlamaIndex query execution** is synchronous by default. `query_engine.query` runs the
full retrieval-synthesis pipeline and returns a `Response` object. Async variants
(`aquery`) are available for integration with async runtimes.

**AutoGen conversation** is event-driven. `initiate_chat` runs a loop that alternates
agent responses until a termination condition is detected. Each iteration is a synchronous
LLM call. The loop has no intrinsic timeout — `max_turns` is the only guard.

**Semantic Kernel invocation** is async throughout. `kernel.invoke_prompt` returns a
coroutine that resolves when the planner has completed all function calls and the model
has emitted a final response.

---

## 6. Integration Points

**Shared infrastructure.** All four frameworks connect to the same underlying
infrastructure: OpenAI-compatible LLM APIs, embedding models, and vector stores. The
framework choice does not change the infrastructure requirements — it changes how those
components are accessed and composed.

**LangChain ↔ LlamaIndex.** LlamaIndex query engines implement the LangChain `Retriever`
interface via `LlamaIndexRetriever`. This allows a LlamaIndex index to be used inside a
LangChain LCEL chain without reimplementing retrieval logic.

**Lab corpus.** The `labs/frameworks-tools/corpus/` directory contains a shared document
set used by `lab-langchain`, `lab-llamaindex`, and `lab-integration`. All retrieval labs
operate on the same corpus so results are directly comparable across frameworks.

---

## 7. Trade-offs and Design Decisions

**Single framework vs. layered frameworks.** Using LangChain for everything (including
retrieval) is simpler to maintain but produces lower-quality retrieval pipelines for
complex corpora. Using LangChain + LlamaIndex in layers adds a dependency but separates
concerns cleanly: LangChain owns orchestration, LlamaIndex owns data.

**Framework abstraction depth vs. debuggability.** LangChain's LCEL adds observable
debuggability through `.with_listeners()` and LangSmith. AutoGen's transcript model makes
agent behavior inspectable by reading the message log. Semantic Kernel's async-first model
requires explicit logging to trace function invocations. Choose the framework that aligns
with the debugging tools your team is already using.

**Shared corpus in labs.** The `corpus/` pattern allows different retrieval labs to
operate on the same documents and produce directly comparable outputs. This is a design
decision that makes the framework comparison observable rather than theoretical.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| LangChain LCEL chain with memory | `lab-langchain` |
| LlamaIndex VectorStoreIndex + QueryEngine | `lab-llamaindex` |
| AutoGen two-agent and GroupChat | `lab-autogen` |
| Semantic Kernel kernel + plugins + planner | `lab-semantic-kernel` |
| LangChain + LlamaIndex integrated pipeline | `lab-integration` |

---

## 9. Limitations and Boundaries

This architecture does not cover:

- LangGraph (graph-based orchestration for complex agentic flows)
- LlamaIndex agentic pipelines (`AgentRunner`, `ReActAgent`)
- AutoGen Studio (visual multi-agent designer)
- Production deployment patterns for framework-based applications (covered in `deployment-scaling`)
- Evaluation of framework pipeline outputs (covered in `evaluation-testing`)

The corpus used in the labs is a small, fixed document set. Index performance and retrieval
quality observations from the labs do not generalize to production-scale corpora without
re-validation.

---

## 10. Summary

AI framework components sit between the application domain logic and the infrastructure
layer. LangChain composes the orchestration pipeline; LlamaIndex structures the retrieval
pipeline; AutoGen coordinates multi-agent conversations; Semantic Kernel integrates AI
capabilities into enterprise service architectures. Each framework wraps the same
underlying LLM and vector store infrastructure through a different abstraction model. The
integration architecture for this module uses LangChain and LlamaIndex in layers connected
to shared infrastructure, with AutoGen and Semantic Kernel as alternative orchestration
layers for their respective use cases.
