---
id: "ai-java-readme"
title: "AI Development in Java"
type: "step-readme"
step: "ai-java"
path: "docs/ai-java/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "Java AI ecosystem"
  - "Spring AI"
  - "LangChain4j"
  - "Java AI pattern"

prerequisites:
  - "docs/frameworks-tools/README.md"

next:
  - "docs/ai-java/java-ai-landscape.md"

related:
  - "docs/frameworks-tools/langchain.md"
  - "docs/frameworks-tools/llamaindex.md"
  - "docs/frameworks-tools/framework-comparison.md"

implementation_refs: []

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Introduces the Java AI ecosystem — Spring AI and LangChain4j — and the patterns Java enterprise engineers use to build LLM-powered applications."
---

# AI Development in Java

## Navigation

[Docs](../README.md) / AI Development in Java

---

## 1. Overview

The previous modules introduced AI development patterns through Python frameworks: LangChain
for orchestration, LlamaIndex for retrieval, AutoGen for multi-agent systems. This module
maps those patterns onto the Java ecosystem.

Java enterprise engineers are not starting from zero. The concepts are the same — prompt
engineering, RAG, tool use, agent loops, memory management. What changes is the execution
context: Spring Boot application context, Maven/Gradle dependency management, strong static
typing, enterprise security infrastructure, and organizational requirements for Java-only
technology stacks.

Two frameworks dominate the Java AI space: **Spring AI**, the official Spring Framework
integration for LLM APIs, and **LangChain4j**, an independent port of the LangChain
abstraction model to Java. Each targets a different point on the spectrum from rapid
prototyping to enterprise integration.

The capability this module unlocks is translating AI engineering knowledge into Java
implementations that fit inside existing Spring Boot applications and enterprise deployment
pipelines.

---

## 2. Scope

**Covered:**
- The Java AI ecosystem: available frameworks, libraries, and their positioning
- Spring AI: model clients, prompt templates, advisors, RAG components, tool calling
- LangChain4j: chains, memory, tools, RAG pipeline, and AI services
- Java-specific patterns: type-safe prompt interfaces, Spring context integration, reactive streams for streaming responses
- Framework selection for Java teams: when to use Spring AI vs LangChain4j vs direct API calls

**Not covered:**
- Python AI framework internals (covered in `frameworks-tools`)
- Java ML frameworks for model training (Deeplearning4j, DJL) — this module focuses on LLM API integration, not model training
- Fine-tuning or custom model deployment in Java
- Production deployment of Java AI services (covered in `deployment-scaling`)
- Evaluation and testing of Java AI pipelines (covered in `evaluation-testing`)

---

## 3. Key Concepts

**Java AI ecosystem** — the set of libraries, frameworks, and infrastructure components
available to Java engineers for building LLM-powered applications, centered on Spring AI
and LangChain4j for API integration and framework-level abstractions.

**Spring AI** — the official Spring Framework project for AI integration, providing a
uniform `ChatClient` abstraction over multiple LLM providers (OpenAI, Anthropic, Ollama,
Azure OpenAI), Spring Boot auto-configuration, and integrations for vector stores, RAG,
and tool calling.

**LangChain4j** — an independent Java library that ports LangChain's chain, memory, RAG,
and agent abstractions to Java, with a type-safe AI service interface that generates
implementations from annotated Java interfaces at build time.

**Java AI pattern** — the set of implementation idioms that Java engineers apply when
building LLM applications: interface-driven AI services, Spring-managed LLM clients,
reactive streaming via Project Reactor, and dependency injection for model configuration.

---

## 4. Concept Map

```text
                    ┌─────────────────────────────────────┐
                    │      Java AI Application Needs        │
                    └──────────────┬──────────────────────┘
                                   │
          ┌────────────────────────┼──────────────────────────┐
          ▼                        ▼                           ▼
 ┌─────────────────┐    ┌──────────────────────┐    ┌────────────────────┐
 │  Spring          │    │  LangChain4j          │    │  Direct API        │
 │  Ecosystem       │    │  (Portable chains,    │    │  (OpenAI Java SDK, │
 │  Integration     │    │   AI Services,        │    │   Anthropic Java   │
 │                  │    │   type-safe RAG)      │    │   SDK)             │
 │  Spring AI       │    │                       │    │                    │
 │  (ChatClient,    │    │                       │    │                    │
 │   Advisors, RAG) │    │                       │    │                    │
 └─────────────────┘    └──────────────────────┘    └────────────────────┘
          │                        │                           │
          └────────────────────────┼──────────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │   Java AI Patterns                    │
                    │   (type-safe interfaces, async,       │
                    │    Spring context, DI)               │
                    └─────────────────────────────────────┘
```

---

## 5. Learning Flow

```text
java-ai-landscape.md     → The Java AI ecosystem: frameworks, libraries, positioning
spring-ai.md             → Spring AI: ChatClient, advisors, RAG, tool calling
langchain4j.md           → LangChain4j: chains, AI services, RAG, memory
java-patterns.md         → Idioms: type-safe AI services, reactive streams, Spring DI
architecture.md          → How Java AI components compose at system level
implementation-reference.md → Patterns and design decisions (concept-only — no runnable labs)
validation.md            → Completion criteria and self-assessment
```

`java-ai-landscape.md` is the required starting point — it establishes the ecosystem
context. `spring-ai.md` and `langchain4j.md` can be read in either order after that.
`java-patterns.md` synthesizes both and should be read last among the topic files.

---

## 6. Documentation Structure

```text
docs/ai-java/
├── README.md                    ← this file
├── java-ai-landscape.md         ← topic: ecosystem overview and framework positioning
├── spring-ai.md                 ← topic: Spring AI components and API
├── langchain4j.md               ← topic: LangChain4j chains, AI services, and RAG
├── java-patterns.md             ← topic: Java-specific implementation patterns
├── architecture.md              ← system architecture
├── implementation-reference.md  ← implementation patterns
└── validation.md                ← completion criteria
```

---

## 7. Labs Overview

This module is concept-only. No executable labs are provided.

The underlying AI concepts — prompt engineering, RAG, tool use, agent loops, memory
management — are demonstrated in the Python labs from earlier modules. The Java-specific
implementations follow the same logic with different syntax and Spring/Maven conventions.

Engineers targeting a Java implementation should read this module to understand the
framework-level abstractions, then implement against a real Spring Boot project. See
`labs/ai-java/README.md` for notes on the concept-only decision.

---

## 8. How to Use This Module

Read `java-ai-landscape.md` first to understand the available options before committing
to a framework. Then read either `spring-ai.md` or `langchain4j.md` depending on your
current project context — both topics are self-contained.

`java-patterns.md` synthesizes the idioms from both frameworks and is the most directly
actionable reference when writing Java AI code. Read it after at least one of the
framework-specific topics.

This module has no labs. Apply the concepts directly to a Spring Boot project or use the
code examples as a reference implementation model.

---

## 9. Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `frameworks-tools` | Spring AI's `ChatClient` maps to LangChain's chain interface; LangChain4j's AI services map to LangChain agent tool use; the RAG components map to LlamaIndex retrieval |
| `rag` | Spring AI and LangChain4j both implement the retrieve-augment-generate pattern introduced there |
| `memory-context` | Both frameworks provide conversation history management over the memory patterns from this module |
| `ai-agents` | LangChain4j's agent interface implements the tool-use loop introduced in this module |
| `evaluation-testing` | Java AI pipelines require the same evaluation techniques; Spring AI supports Testcontainers-based integration testing |

---

## 10. Next Steps

Begin with `docs/ai-java/java-ai-landscape.md` to understand how the Java ecosystem
maps to the Python frameworks already covered, and where the two ecosystems diverge.

---

## 11. Engineering Takeaways

### What This Adds

Java-native AI integration patterns — translating the Python-centric RAG, tool use, memory, and agent loop patterns into Spring Boot applications and enterprise Java deployment pipelines. The underlying concepts are identical; what changes is the execution context, type system, and organizational constraints.

### Engineering Trade-offs

| Decision | Benefit | Cost | When it breaks |
|----------|---------|------|----------------|
| Spring AI vs LangChain4j | Spring AI integrates with Spring Boot DI and auto-configuration; LangChain4j provides portable chains and type-safe AI service interfaces | Spring AI ties you to the Spring ecosystem; LangChain4j has a smaller community than Python LangChain | Spring AI version lags behind new provider APIs; LangChain4j AI service interface generation fails on complex type hierarchies |
| Spring AI `ChatClient` vs direct SDK calls | Auto-configured; provider-switchable via properties | Abstraction hides provider-specific features; harder to debug low-level issues | Provider-specific capabilities (extended thinking, structured outputs with JSON schema) not yet exposed by Spring AI |
| Reactive streaming vs blocking | Non-blocking throughput under load; Project Reactor integration | Debugging reactive pipelines requires familiarity with Flux/Mono; stack traces are non-linear | Team is not familiar with Project Reactor; streaming response must be consumed synchronously |
| Interface-driven AI services (LangChain4j) | Type-safe; testable; Spring-injectable | Generated at build time; harder to inspect what the framework sends to the API | Annotation-based behavior does not match expected model behavior; debugging requires inspecting generated prompts |

### When NOT to Use This

- When the team is delivering on a Python platform — do not add Java just to match the existing module coverage.
- When Spring AI or LangChain4j have not yet implemented the provider feature you need — verify API coverage before committing to a framework.
- When the Java service is a thin adapter over a Python-based AI backend — call the Python service directly rather than reimplementing the pipeline in Java.

### Common Failure Modes

- **Failure:** Spring context startup fails because LLM client bean cannot be auto-configured.
  **Cause:** Missing API key property, wrong property name, or incompatible Spring Boot version.
  **Signal:** `NoSuchBeanDefinitionException` or `BeanCreationException` for the `ChatClient` or embedding model bean.

- **Failure:** Streaming response is consumed incorrectly and produces a truncated result.
  **Cause:** `Flux<String>` subscribed with `blockFirst()` instead of `collectList().block()` or proper reactive composition.
  **Signal:** Only the first token is captured; rest of the response is dropped.

- **Failure:** LangChain4j AI service returns unexpected null or empty results.
  **Cause:** Annotated interface method return type does not match what the model produces; extraction fails silently.
  **Signal:** Method returns null or an empty object; no exception thrown; model response is discarded.

### What Changes vs Traditional Systems

The shift is not conceptual — the AI patterns are the same as in Python. What changes is integration surface: dependency injection manages model clients, Spring Boot auto-configuration handles provider setup, and the type system enforces structure at compile time. Java engineers familiar with Spring already know the integration model; the new discipline is understanding what the AI framework does at the API boundary.

### Operational Considerations

- Required: Spring Boot application context; API key management via Spring properties or secrets manager; `requirements.txt` equivalent via Maven/Gradle dependencies with pinned versions.
- Observable: API call latency via Spring Boot Actuator metrics, streaming throughput, Spring AI retry events.
- Cost drivers: same as the underlying provider; Spring AI may add retries that multiply call volume.
- Debugging: enable `logging.level.org.springframework.ai=DEBUG` to inspect prompts and responses at the framework boundary.
- Scaling: reactive streaming scales well under load; blocking calls limit throughput to thread pool size.

### Minimal Adoption Heuristic

**Use this when:**
- The organization mandates Java or the AI component must integrate into an existing Spring Boot application.
- The team already operates Spring Boot services and wants to add AI capabilities without introducing a Python runtime.

**Avoid this when:**
- There is no organizational constraint requiring Java — the Python ecosystem has more mature tooling and broader framework support.
- The use case requires framework features that Spring AI or LangChain4j do not yet implement — verify coverage before committing.
