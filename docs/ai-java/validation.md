---
id: "ai-java-validation"
title: "AI Development in Java — Validation"
type: "validation"
step: "ai-java"
path: "docs/ai-java/validation.md"
status: "draft"
level: "intermediate"

concepts:
  - "Java AI ecosystem"
  - "Spring AI"
  - "LangChain4j"
  - "AI service"
  - "advisor"
  - "Java AI pattern"

prerequisites:
  - "docs/ai-java/implementation-reference.md"

next:
  - "docs/evaluation-testing/README.md"

related:
  - "docs/ai-java/README.md"
  - "docs/frameworks-tools/validation.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Defines the completion criteria and self-assessment checklist for the ai-java module."
---

# AI Development in Java — Validation

## Navigation

[Docs](../README.md) / [AI Development in Java](README.md) / AI Development in Java — Validation

---

## 1. Validation Overview

This module covers the Java AI ecosystem as a concept-only study. There are no executable
labs. Mastery is demonstrated by the ability to select between Spring AI and LangChain4j
for a given context, explain the architecture of each, design the interface and component
structure for a Java AI application, and identify common failure modes before
implementation.

The target audience — Java enterprise architects — already has deep Java and Spring
knowledge. Validation therefore focuses on the mapping from AI concepts (already covered
in prior modules) to Java-specific implementations, not on re-explaining the underlying AI
patterns.

---

## 2. Conceptual Validation

| Concept | Validation method |
|---------|------------------|
| Java AI ecosystem | Identify the three layers (provider SDKs, framework layer, infrastructure support) and name at least one tool at each layer |
| Spring AI | Explain the role of `ChatClient`, at least two built-in advisors, and how the advisor chain maps to the Python LCEL pipeline |
| LangChain4j | Explain the AI service interface pattern: what it declares, how LangChain4j generates the implementation, and what the builder configures |
| Advisor chain | Describe the execution order and explain why memory must be registered before RAG in the advisor chain |
| `ChatMemoryProvider` | Explain why a per-session-id memory provider is required for multi-user applications, and what goes wrong with a shared instance |
| AI service interface | Given a use case description, write a correct `interface` declaration with appropriate annotations (`@SystemMessage`, `@UserMessage`, `@MemoryId`) |
| Java AI pattern | Identify which Java pattern applies to: (1) testability, (2) environment portability, (3) structured output, (4) streaming |
| Framework selection | State the decision criterion for Spring AI vs LangChain4j and give a concrete example where each is the correct choice |

---

## 3. Practical Validation

**Task 1: Interface design**

```text
Scenario: A customer support application needs an AI assistant with:
- A consistent system persona ("You are a support agent for Acme Corp.")
- Per-conversation memory (last 15 messages)
- RAG over a product documentation corpus
- A tool that looks up order status from a database

Task: Write the LangChain4j AI service interface declaration.
Include: @SystemMessage, correct parameter annotations, return type.
Identify: which builder methods wire memory, RAG, and tools.
```

**Task 2: Spring AI pipeline design**

```text
Scenario: A Spring Boot 3.2 application needs a conversational endpoint that:
- Maintains conversation history per authenticated user
- Retrieves relevant documents from a pgvector store
- Logs all requests and responses for compliance
- Streams the response to the browser via SSE

Task: List the advisors needed, their order, and the controller return type.
Identify: which Spring AI starters are required.
```

**Task 3: Environment routing**

```text
Scenario: Development uses Ollama with mistral:7b.
          Staging uses OpenAI gpt-4o-mini.
          Production uses OpenAI gpt-4o.

Task: Describe the Spring configuration structure (profiles and properties)
that selects the correct model per environment without conditional code
in the application layer.
```

**Task 4: Failure analysis**

```text
Scenario: A production Spring AI application with RedisChatMemory is deployed
across 3 instances. Users on long conversations report that the assistant
"forgets" earlier messages.

Task: Diagnose the cause. Identify the component responsible.
Explain what is happening at the data flow level.
```

---

## 4. Lab Validation

This module has no executable labs. Validate implementation understanding by applying
the patterns to a Spring Boot project. The minimum viable implementation for each topic:

| Topic | Minimum implementation |
|-------|----------------------|
| Spring AI | `ChatClient` with `MessageChatMemoryAdvisor`; respond to a multi-turn question |
| LangChain4j | AI service interface with `@SystemMessage` and `@MemoryId`; run two consecutive turns |
| RAG (Spring AI) | `QuestionAnswerAdvisor` with an in-memory `SimpleVectorStore`; retrieve and answer from 3 documents |
| RAG (LangChain4j) | `EmbeddingStoreContentRetriever` with an in-memory embedding store; retrieve and answer from 3 documents |
| Tool calling | `@Tool`-annotated method returning a fixed string; verify the model invokes it and incorporates the result |

---

## 5. Integration Validation

A Java AI application integrates concepts from multiple prior modules. Validate that these
connections are clear:

**Memory (from `memory-context`):** `MessageWindowChatMemory` implements the conversation
buffer pattern. `TokenWindowChatMemory` implements the sliding token window. The memory
ID maps to the session key pattern. The persistence strategies (in-memory vs Redis) map
to the external memory patterns.

**RAG (from `rag`):** `VectorStore` / `EmbeddingStore` implements the vector search
component. `DocumentReader` + `TextSplitter` / `EmbeddingStoreIngestor` implement the
ingestion pipeline. The advisor or content retriever implements the retrieve-then-inject
assembly pattern.

**Tool use (from `ai-agents`):** `@Tool` method declaration implements the tool registry.
The AI service proxy or Spring AI tool handling implements the tool-use loop
(call → parse → dispatch → resubmit).

**Structured output (from `structured-outputs`):** `.entity(Class)` and typed AI service
return types implement the JSON schema enforcement pattern using Java record definitions.

---

## 6. Failure Detection

**Selecting Spring AI without verifying Spring Boot version.** Spring AI requires Spring
Boot 3.x and Java 17. A team on Spring Boot 2.x will encounter `ClassNotFoundException`
errors at startup, not compile-time.

**Treating `@SystemMessage` as code documentation.** The `@SystemMessage` annotation is
model instruction, not code documentation. It is sent to the LLM on every call. Vague,
incomplete, or contradictory system messages produce inconsistent model behavior, not
compilation errors.

**Missing `@MemoryId` on multi-user interface.** An AI service interface without `@MemoryId`
on the session parameter will either use a shared global memory (mixing conversations) or
ignore the parameter (no memory). Both are silent bugs — the application compiles and runs
but produces incorrect behavior.

**Not validating structured output.** `IntentResult classify(String text)` deserializes
the model's JSON response into a Java record. If the model produces invalid JSON or omits
a required field, Jackson throws at deserialization, not at the model call. Add validation
on the returned record before using it downstream.

---

## 7. Completion Criteria

The ai-java module is complete when:

- The three layers of the Java AI ecosystem can be named and described
- The difference between Spring AI's advisor chain and LangChain4j's AI service proxy can be explained in terms of where pipeline logic lives
- A LangChain4j AI service interface can be designed correctly for a given requirement (system prompt, memory, RAG, tools)
- A Spring AI advisor registration can be designed correctly with appropriate ordering
- The framework selection criterion (Spring Boot vs framework-portable context) can be applied to a concrete scenario
- The memory ID isolation pattern is understood and its failure mode can be described
- All practical validation tasks (section 3) can be reasoned through without external reference

---

## 8. Self-Assessment Checklist

```text
Java AI Ecosystem
- [ ] I can name the two primary Java AI frameworks and their integration targets
- [ ] I understand why Java AI frameworks exist (runtime constraints, Spring ecosystem)
- [ ] I know the Java AI ecosystem's maturity limitations relative to Python

Spring AI
- [ ] I can explain what ChatClient does and how it differs from ChatModel
- [ ] I can name three built-in advisors and describe what each adds to the pipeline
- [ ] I understand advisor ordering and why it matters
- [ ] I can describe how Spring profiles route to different model providers

LangChain4j
- [ ] I can write a correct AI service interface with @SystemMessage, @UserMessage, @MemoryId
- [ ] I know what each AiServices builder method configures
- [ ] I understand why ChatMemoryProvider takes a session ID function, not a singleton

Java AI Patterns
- [ ] I can identify which pattern applies to testability, environment routing, and streaming
- [ ] I understand the trade-off between annotation-driven (LangChain4j) and builder-driven (Spring AI) configuration
- [ ] I can describe the token usage tracking pattern

Framework Selection
- [ ] I can apply the Spring AI vs LangChain4j selection criterion to a scenario
- [ ] I can identify when a direct provider SDK is the right choice
```

---

## 9. Next Steps

**If validation passes:** Proceed to `docs/evaluation-testing/README.md`. The evaluation
module applies to Java AI pipelines as well as Python ones — testing strategies, mocking
LLM clients, and contract testing apply directly to the Spring AI and LangChain4j patterns
covered here.

**If validation needs reinforcement:**

| Gap | Revisit |
|-----|---------|
| Uncertain about advisor pattern | `docs/ai-java/spring-ai.md` section 2.2 (Advisors) |
| Uncertain about AI service interface | `docs/ai-java/langchain4j.md` section 2.2 (AI service) |
| Uncertain about framework selection | `docs/ai-java/java-ai-landscape.md` table, section 4 |
| Uncertain about Java patterns | `docs/ai-java/java-patterns.md` section 2.2 (pattern catalog) |
| Uncertain about integration with prior modules | `docs/ai-java/architecture.md` section 6 (Integration Points) |
