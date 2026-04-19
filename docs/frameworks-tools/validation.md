---
id: "frameworks-tools-validation"
title: "Frameworks and Tools — Validation"
type: "validation"
step: "frameworks-tools"
path: "docs/frameworks-tools/validation.md"
status: "draft"
level: "intermediate"

concepts:
  - "LangChain"
  - "LlamaIndex"
  - "AutoGen"
  - "Semantic Kernel"
  - "framework selection"
  - "pipeline composition"

prerequisites:
  - "docs/frameworks-tools/implementation-reference.md"

next:
  - "docs/ai-java/README.md"

related:
  - "docs/frameworks-tools/README.md"
  - "docs/frameworks-tools/framework-comparison.md"

implementation_refs:
  - "labs/frameworks-tools/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines the completion criteria and self-assessment checklist for the frameworks-tools module."
---

# Frameworks and Tools — Validation

## Navigation

[Docs](../README.md) / [Frameworks and Tools](README.md) / Frameworks and Tools — Validation

---

## 1. Validation Overview

This module introduces four distinct frameworks with distinct abstractions. Completion
requires both conceptual mastery — understanding why each framework's abstraction exists —
and practical execution of the required labs. A learner who can run the labs but cannot
explain the selection criteria is not ready to move forward. A learner who can explain the
frameworks but has not observed them at runtime will not catch the failure modes that only
appear under execution.

---

## 2. Conceptual Validation

| Concept | Validation Method |
|---------|-------------------|
| LangChain / LCEL | Explain what a Runnable is, how LCEL composes Runnables, and why LCEL replaces legacy chain classes |
| LangChain memory | Explain how `RunnableWithMessageHistory` reads and writes history and why context limits require explicit management |
| LlamaIndex nodes and index | Explain the Document → Node → Index pipeline and why index construction is separated from query execution |
| LlamaIndex query engine | Explain the retrieval → postprocessing → synthesis flow and the trade-offs between response modes |
| AutoGen conversation model | Explain why the transcript is the shared state and what happens when `max_turns` is not set |
| AutoGen GroupChat | Explain how the GroupChatManager selects speakers and why LLM-based selection is non-deterministic |
| Semantic Kernel kernel and plugins | Explain the difference between a semantic function and a native function and why function descriptions must be precise |
| Semantic Kernel planner | Explain how `FunctionChoiceBehavior` selects functions and what happens when the description is vague |
| Framework selection | Given a use case description, identify the appropriate framework and justify the choice |

---

## 3. Practical Validation

```text
Task: Build a LangChain LCEL chain that retrieves documents, assembles a context,
      and answers a question with session memory.
Expected: Chain uses a Retriever step, a ChatPromptTemplate with a context slot,
          and RunnableWithMessageHistory. Invoking with the same session_id twice
          preserves prior conversation context.

Task: Build a LlamaIndex retrieval pipeline over the shared corpus.
Expected: Index is constructed with SentenceSplitter, persisted to ChromaDB,
          reloaded without re-ingesting, and queried with a configurable top_k.
          Changing top_k changes the retrieved nodes and the response quality.

Task: Explain why using LangChain for complex retrieval pipelines is less optimal
      than using LlamaIndex.
Expected: Identifies that LangChain's Retriever interface is generic and lacks
          node-level metadata management, incremental indexing, and response mode control.
```

---

## 4. Lab Validation

| Lab | Validation Criteria |
|-----|---------------------|
| `lab-langchain` | LCEL chain runs end-to-end; memory persists context across two invocations with the same session ID; agent dispatches at least one tool call and returns a final answer |
| `lab-llamaindex` | Index built from corpus, persisted, reloaded; query engine returns a response with source node metadata; changing `similarity_top_k` produces observably different results |
| `lab-autogen` *(optional)* | Two-agent conversation terminates cleanly; tool call is dispatched by UserProxyAgent and result is returned to AssistantAgent |
| `lab-semantic-kernel` *(optional)* | Plugin registered; planner selects the correct function for a given prompt; async invocation completes without errors |
| `lab-integration` *(optional)* | LangChain chain wraps a LlamaIndex retriever; end-to-end pipeline returns a response with provenance from the corpus |

---

## 5. Integration Validation

A learner who has completed this module should be able to reason about the following
integration scenarios:

**Scenario 1:** A team needs to build a customer support assistant that retrieves answers
from a knowledge base of 50,000 documents and maintains conversation history per user.
Which framework(s) would you use and why?

Expected reasoning: LlamaIndex for retrieval (document scale, metadata management,
persistent indexing) + LangChain for orchestration (conversation memory, chain
composition). The two frameworks are used at separate layers.

**Scenario 2:** A team needs to automate a code review workflow where a reviewer agent
analyzes a pull request, a security agent checks for vulnerabilities, and a summary agent
produces a final report.
Which framework would you use?

Expected reasoning: AutoGen, because the use case is multi-agent coordination through
structured conversation. Each agent has a distinct role and the transcript carries all
intermediate state. LangChain's AgentExecutor handles single-agent tool use but does not
model multi-agent dialogue natively.

**Scenario 3:** A .NET enterprise team wants to add an AI summarization capability to an
existing C# microservice without rewriting the service.
Which framework would you use?

Expected reasoning: Semantic Kernel. It provides native C# and Python SDKs, a plugin model
that maps to existing service boundaries, and a planner that composes plugins without
requiring framework-specific orchestration code.

---

## 6. Failure Detection

**Misuse of LangChain for data-intensive RAG.** Using `LangChain.retriever` with a raw
vector store for a 50,000-document corpus produces adequate results for simple queries but
does not handle metadata filtering, incremental updates, or hierarchical retrieval. The
failure appears at scale, not in prototyping.

**Using AutoGen for single-agent tasks.** AutoGen's conversation abstraction adds overhead
when the task requires only one agent. A single `AssistantAgent` wrapping a model with
tools is functionally equivalent to a LangChain AgentExecutor but with a heavier
conversation management layer.

**Semantic Kernel function descriptions that are too generic.** A native function
described as "processes data" is never selected by the planner for any specific task
because the description does not match any concrete user query. Write descriptions as
precise capability statements.

**Ignoring framework version pins.** LangChain and LlamaIndex have made breaking API
changes across minor releases. Importing `from langchain.chains import LLMChain` in
LangChain 0.2.x raises a deprecation warning and fails in 0.3.x. All labs pin versions
in `requirements.txt` for this reason.

---

## 7. Completion Criteria (MANDATORY)

This module is complete when:

- The learner can explain the primary abstraction of each framework (Runnable, Index, ConversableAgent, Kernel) and why it exists
- `lab-langchain` and `lab-llamaindex` execute successfully and produce the expected outputs
- The learner can apply the selection criteria from `framework-comparison.md` to choose a framework for a described use case
- The learner can identify at least one failure mode for each required framework

---

## 8. Self-Assessment Checklist

```text
- [ ] I can explain what a LangChain Runnable is and how LCEL composes Runnables
- [ ] I can build a LangChain LCEL chain with retrieval and session memory
- [ ] I can explain the LlamaIndex Document → Node → Index pipeline
- [ ] I can build a LlamaIndex retrieval pipeline over a document corpus
- [ ] I can run lab-langchain end-to-end and observe memory persistence across turns
- [ ] I can run lab-llamaindex and observe how changing top_k affects results
- [ ] I can explain when AutoGen is the right choice over LangChain agents
- [ ] I can explain why Semantic Kernel is designed for enterprise integration
- [ ] I can select the right framework given a use case and justify the choice
- [ ] I can identify the failure mode that arises from using the wrong framework
```

---

## 9. Next Steps

**If validation fails:** Return to the topic that corresponds to the weak area. For LCEL
confusion, re-read `langchain.md` and run `lab-langchain` with explicit logging to observe
each step. For retrieval confusion, re-read `llamaindex.md` and compare `similarity_top_k`
values in `lab-llamaindex`.

**If validation passes:** Proceed to `docs/ai-java/README.md` to apply AI engineering
patterns in a Java context with Spring AI and LangChain4j.
