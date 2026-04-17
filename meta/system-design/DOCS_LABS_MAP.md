# DOCS_LABS_MAP.md

## Purpose

This document defines the canonical mapping between documentation modules and lab
implementations. It also establishes the order in which modules should be studied.

Module folder names have no numeric prefix. This document is the authoritative
source for module sequence and docs-to-labs alignment.

---

## Reference Content (cross-module, no sequence)

Content under `docs/reference/` is not part of the module sequence. It has no labs
and no learning order. It is consulted throughout the entire tutorial.

| File | Purpose | Labs |
|------|---------|------|
| `docs/reference/glossary.md` | Canonical term definitions | none |

---

## Module Sequence

| Order | Module | Level |
|-------|--------|-------|
| 1 | `llm-fundamentals` | Foundational |
| 2 | `llm-apis` | Foundational |
| 3 | `prompt-engineering` | Foundational |
| 4 | `structured-outputs` | Intermediate |
| 5 | `rag` | Intermediate |
| 6 | `memory-context` | Intermediate |
| 7 | `ai-agents` | Intermediate |
| 8 | `frameworks-tools` | Intermediate |
| 9 | `ai-java` | Intermediate |
| 10 | `evaluation-testing` | Advanced |
| 11 | `safety-guardrails` | Advanced |
| 12 | `performance-optimization` | Advanced |
| 13 | `deployment-scaling` | Advanced |
| 14 | `observability-mlops` | Advanced |
| 15 | `reference-architectures` | Advanced |
| 16 | `real-world-projects` | Advanced |

---

## Mapping Types

| Type | When to use |
|------|-------------|
| `concept-only` | Foundational or explanatory topic, no runnable demonstration needed |
| `observation` | Concept benefits from runtime observation but not deep implementation |
| `implementation` | Core engineering capability that must be practiced |
| `integration` | Several topics converge into one larger system behavior |
| `module-integration` | Module-level lab tied to `architecture.md` — shows how all concepts in the module compose at runtime |
| `project` | Full end-to-end project (module 16 only) |

---

## Decision Rule

Every topic file must have one explicit mapping decision:

- `required` → lab must exist before module is considered complete
- `optional` → lab exists but is not a blocker
- `none` → no lab needed, concept-only

Core engineering topics must not remain unmapped.

---

## Module-Level Artifacts

In addition to `lab-<n>/` folders and `shared/`, a module may include:

| Artifact | Path | When to use |
|----------|------|-------------|
| `corpus/` | `labs/<module>/corpus/` | Multiple labs operate on the same fixed document set and the learner should read the files before running the labs. See `lab-code-style.md §9` for the full convention. |

A module that uses `corpus/` must document it in its `labs/<module>/README.md`.

Modules with a `corpus/`:

| Module | Status |
|--------|--------|
| `rag` | ✅ exists |
| `frameworks-tools` | ⬜ pending |
| `evaluation-testing` | ⬜ pending |

---

## Module Maps

### llm-fundamentals

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `llm-architecture.md` | `lab-llm-anatomy` | observation | required |
| `tokenization.md` | `lab-tokenization` | observation | required |
| `context-window.md` | `lab-context-window` | observation | required |
| `inference-parameters.md` | `lab-inference-parameters` | observation | required |
| `fine-tuning.md` | — | concept-only | none |
| `multimodality.md` | — | concept-only | none |

---

### llm-apis

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `openai-api.md` | `lab-openai-api` | implementation | required |
| `ollama-api.md` | `lab-ollama-api` | implementation | required |
| `anthropic-api.md` | `lab-anthropic-api` | implementation | required |
| `streaming.md` | `lab-streaming` | implementation | required |
| `api-patterns.md` | `lab-api-patterns` | implementation | optional |

---

### prompt-engineering

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `prompt-anatomy.md` | `lab-prompt-anatomy` | observation | required |
| `few-shot.md` | `lab-few-shot` | implementation | required |
| `chain-of-thought.md` | `lab-chain-of-thought` | implementation | required |
| `prompt-patterns.md` | `lab-prompt-patterns` | implementation | required |
| `prompt-pitfalls.md` | — | concept-only | none |
| `architecture.md` | `lab-integration` | module-integration | optional |

---

### structured-outputs

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `structured-outputs.md` | `lab-structured-outputs` | implementation | required |
| `tool-usage.md` | `lab-tool-usage` | implementation | required |
| `tool-patterns.md` | `lab-tool-patterns` | implementation | required |
| `schema-design.md` | `lab-schema-design` | implementation | optional |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### rag

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `rag-fundamentals.md` | — | concept-only | none |
| `embeddings-and-vector-search.md` | `lab-embeddings` | implementation | required |
| `document-processing-and-chunking.md` | `lab-chunking-strategies` | implementation | required |
| `retrieval-strategies.md` | `lab-retrieval-playground` | implementation | required |
| `context-assembly.md` | `lab-query-pipeline` | implementation | required |
| `rag-evaluation-and-metrics.md` | `lab-rag-evaluation` | implementation | required |
| `architecture.md` | `lab-integration` | module-integration | required |

> `lab-query-pipeline` covers partial integration (retrieval + context assembly). `lab-integration` covers the full RAG pipeline end-to-end including chunking, indexing, retrieval, assembly, and generation.

---

### memory-context

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `memory-types.md` | `lab-memory-types` | observation | required |
| `conversation-history.md` | `lab-conversation-history` | implementation | required |
| `context-management.md` | `lab-context-management` | implementation | required |
| `external-memory.md` | `lab-external-memory` | implementation | optional |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### ai-agents

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `agent-fundamentals.md` | — | concept-only | none |
| `single-agent-loop.md` | `lab-single-agent-loop` | implementation | required |
| `tool-use-loops.md` | `lab-tool-use-loops` | implementation | required |
| `multi-agent-systems.md` | `lab-multi-agent` | integration | required |
| `agent-patterns.md` | `lab-agent-patterns` | implementation | optional |
| `mcp.md` | `lab-mcp-server` | implementation | required |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### frameworks-tools

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `langchain.md` | `lab-langchain` | implementation | required |
| `llamaindex.md` | `lab-llamaindex` | implementation | required |
| `autogen.md` | `lab-autogen` | implementation | optional |
| `semantic-kernel.md` | `lab-semantic-kernel` | implementation | optional |
| `framework-comparison.md` | — | concept-only | none |
| `workflow-tools.md` | — | concept-only | none |
| `architecture.md` | `lab-integration` | module-integration | optional |

---

### ai-java

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `java-ai-landscape.md` | — | concept-only | none |
| `spring-ai.md` | — | concept-only | none |
| `langchain4j.md` | — | concept-only | none |
| `java-patterns.md` | — | concept-only | none |

> No labs planned for this module. See `labs/ai-java/README.md`.

---

### evaluation-testing

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `evaluation-fundamentals.md` | — | concept-only | none |
| `llm-evaluation-metrics.md` | `lab-evaluation-metrics` | implementation | required |
| `application-testing.md` | `lab-application-testing` | implementation | required |
| `mocking-and-integration.md` | `lab-mocking` | implementation | required |
| `contract-testing.md` | `lab-contract-testing` | implementation | optional |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### safety-guardrails

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `safety-fundamentals.md` | — | concept-only | none |
| `input-guardrails.md` | `lab-input-guardrails` | implementation | required |
| `output-guardrails.md` | `lab-output-guardrails` | implementation | required |
| `vulnerabilities.md` | `lab-red-teaming` | observation | required |
| `red-teaming.md` | `lab-red-teaming` | implementation | required |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### performance-optimization

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `latency-and-throughput.md` | `lab-latency-benchmarks` | observation | required |
| `caching-strategies.md` | `lab-caching` | implementation | required |
| `prompt-optimization.md` | `lab-prompt-optimization` | implementation | required |
| `model-selection.md` | — | concept-only | none |
| `batching.md` | `lab-batching` | implementation | optional |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### deployment-scaling

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `deployment-patterns.md` | — | concept-only | none |
| `containerization.md` | `lab-containerization` | implementation | required |
| `api-gateway.md` | `lab-api-gateway` | implementation | required |
| `scaling-strategies.md` | `lab-scaling` | implementation | optional |
| `infrastructure-as-code.md` | `lab-iac` | implementation | optional |

> **Scope note:** `deployment-patterns.md` or `scaling-strategies.md` must explicitly cover
> async LLM workload patterns: task queues (e.g. Celery, ARQ), message brokers (e.g. Redis,
> RabbitMQ), and webhook/callback patterns for long-running generations. These are the
> production-grade alternatives to synchronous streaming when clients may disconnect,
> generation time exceeds HTTP timeouts, or multiple consumers need to receive results.
> Origin: decision from `llm-apis` module review (2026-04-15).

---

### observability-mlops

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `observability-fundamentals.md` | — | concept-only | none |
| `tracing-and-logging.md` | `lab-tracing` | implementation | required |
| `prompt-versioning.md` | `lab-prompt-versioning` | implementation | required |
| `continuous-evaluation.md` | `lab-continuous-eval` | implementation | required |
| `mlops-patterns.md` | — | concept-only | none |
| `architecture.md` | `lab-integration` | module-integration | required |

---

### reference-architectures

| Doc | Lab | Type | Decision |
|-----|-----|------|----------|
| `pattern-map.md` | — | concept-only | none |
| `rag-system.md` | — | concept-only | none |
| `agent-system.md` | — | concept-only | none |
| `multi-agent-platform.md` | — | concept-only | none |
| `production-llm-api.md` | — | concept-only | none |
| `mcp-server.md` | — | concept-only | none |

---

### real-world-projects

| Project | Language | Description |
|---------|----------|-------------|
| `rag-assistant` | Python | End-to-end RAG application |
| `agent-workflow` | Python | Multi-tool agent system |
| `java-rag-assistant` | Java | RAG variant using Spring AI |
| `mcp-enterprise-server` | Python | MCP server exposing enterprise tools to an agent |
