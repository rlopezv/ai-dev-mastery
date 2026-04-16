# WORKPLAN.md

Tracks all work units for the AI Dev Mastery tutorial, from first module to final project.
May be updated alongside `PROJECT_STATUS.md`, but does not define canonical completion status.

**Legend:** ⬜ not started · 🔄 in progress · ✅ complete

## Role

This file is an **internal execution tracker**.

- It is NOT a source of truth for completion status
- It may contain incomplete, manual, or exploratory work
- It is maintained as a working document during repository construction

Canonical project status is defined in:

→ `meta/session/PROJECT_STATUS.md`


---

## How to use this file

Each module has two work blocks: **Docs** and **Labs**.
Docs must be complete before Labs begin for the same module.
Work through modules in sequence (1 → 16).

Within each Docs block, write in this order:
`README → topics (per sequence below) → architecture → implementation-reference → validation`

Within each Labs block, write in this order:
`labs/README → labs in sequence`

---

## Phase 1 — Foundational modules

### 1. llm-fundamentals

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 1.1 | `docs/llm-fundamentals/README.md` | step-readme | ⬜ |
| 1.2 | `docs/llm-fundamentals/llm-architecture.md` | topic | ⬜ |
| 1.3 | `docs/llm-fundamentals/tokenization.md` | topic | ⬜ |
| 1.4 | `docs/llm-fundamentals/context-window.md` | topic | ⬜ |
| 1.5 | `docs/llm-fundamentals/inference-parameters.md` | topic | ⬜ |
| 1.6 | `docs/llm-fundamentals/fine-tuning.md` | topic | ⬜ |
| 1.7 | `docs/llm-fundamentals/multimodality.md` | topic | ⬜ |
| 1.8 | `docs/llm-fundamentals/architecture.md` | architecture | ⬜ |
| 1.9 | `docs/llm-fundamentals/implementation-reference.md` | implementation-reference | ⬜ |
| 1.10 | `docs/llm-fundamentals/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 1.L1 | `labs/llm-fundamentals/README.md` | lab-readme | ⬜ |
| 1.L2 | `labs/llm-fundamentals/lab-llm-anatomy/` | observation | ⬜ |
| 1.L3 | `labs/llm-fundamentals/lab-tokenization/` | observation | ⬜ |
| 1.L4 | `labs/llm-fundamentals/lab-context-window/` | observation | ⬜ |
| 1.L5 | `labs/llm-fundamentals/lab-inference-parameters/` | observation | ⬜ |

---

### 2. llm-apis

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 2.1 | `docs/llm-apis/README.md` | step-readme | ⬜ |
| 2.2 | `docs/llm-apis/openai-api.md` | topic | ⬜ |
| 2.3 | `docs/llm-apis/ollama-api.md` | topic | ⬜ |
| 2.4 | `docs/llm-apis/anthropic-api.md` | topic | ⬜ |
| 2.5 | `docs/llm-apis/streaming.md` | topic | ⬜ |
| 2.6 | `docs/llm-apis/api-patterns.md` | topic | ⬜ |
| 2.7 | `docs/llm-apis/architecture.md` | architecture | ⬜ |
| 2.8 | `docs/llm-apis/implementation-reference.md` | implementation-reference | ⬜ |
| 2.9 | `docs/llm-apis/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 2.L1 | `labs/llm-apis/README.md` | lab-readme | ⬜ |
| 2.L2 | `labs/llm-apis/lab-openai-api/` | implementation | ⬜ |
| 2.L3 | `labs/llm-apis/lab-ollama-api/` | implementation | ⬜ |
| 2.L4 | `labs/llm-apis/lab-anthropic-api/` | implementation | ⬜ |
| 2.L5 | `labs/llm-apis/lab-streaming/` | implementation | ⬜ |
| 2.L6 | `labs/llm-apis/lab-api-patterns/` | implementation (optional) | ⬜ |

---

### 3. prompt-engineering

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 3.1 | `docs/prompt-engineering/README.md` | step-readme | ⬜ |
| 3.2 | `docs/prompt-engineering/prompt-anatomy.md` | topic | ⬜ |
| 3.3 | `docs/prompt-engineering/few-shot.md` | topic | ⬜ |
| 3.4 | `docs/prompt-engineering/chain-of-thought.md` | topic | ⬜ |
| 3.5 | `docs/prompt-engineering/prompt-patterns.md` | topic | ⬜ |
| 3.6 | `docs/prompt-engineering/prompt-pitfalls.md` | topic | ⬜ |
| 3.7 | `docs/prompt-engineering/architecture.md` | architecture | ⬜ |
| 3.8 | `docs/prompt-engineering/implementation-reference.md` | implementation-reference | ⬜ |
| 3.9 | `docs/prompt-engineering/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 3.L1 | `labs/prompt-engineering/README.md` | lab-readme | ⬜ |
| 3.L2 | `labs/prompt-engineering/lab-prompt-anatomy/` | observation | ⬜ |
| 3.L3 | `labs/prompt-engineering/lab-few-shot/` | implementation | ⬜ |
| 3.L4 | `labs/prompt-engineering/lab-chain-of-thought/` | implementation | ⬜ |
| 3.L5 | `labs/prompt-engineering/lab-prompt-patterns/` | implementation | ⬜ |

---

### 4. structured-outputs

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 4.1 | `docs/structured-outputs/README.md` | step-readme | ⬜ |
| 4.2 | `docs/structured-outputs/structured-outputs.md` | topic | ⬜ |
| 4.3 | `docs/structured-outputs/tool-usage.md` | topic | ⬜ |
| 4.4 | `docs/structured-outputs/tool-patterns.md` | topic | ⬜ |
| 4.5 | `docs/structured-outputs/schema-design.md` | topic | ⬜ |
| 4.6 | `docs/structured-outputs/architecture.md` | architecture | ⬜ |
| 4.7 | `docs/structured-outputs/implementation-reference.md` | implementation-reference | ⬜ |
| 4.8 | `docs/structured-outputs/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 4.L1 | `labs/structured-outputs/README.md` | lab-readme | ⬜ |
| 4.L2 | `labs/structured-outputs/lab-structured-outputs/` | implementation | ⬜ |
| 4.L3 | `labs/structured-outputs/lab-tool-usage/` | implementation | ⬜ |
| 4.L4 | `labs/structured-outputs/lab-tool-patterns/` | implementation | ⬜ |
| 4.L5 | `labs/structured-outputs/lab-schema-design/` | implementation (optional) | ⬜ |

---

## Phase 2 — Intermediate modules

### 5. rag

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 5.1 | `docs/rag/README.md` | step-readme | ⬜ |
| 5.2 | `docs/rag/rag-fundamentals.md` | topic | ⬜ |
| 5.3 | `docs/rag/embeddings-and-vector-search.md` | topic | ⬜ |
| 5.4 | `docs/rag/document-processing-and-chunking.md` | topic | ⬜ |
| 5.5 | `docs/rag/retrieval-strategies.md` | topic | ⬜ |
| 5.6 | `docs/rag/context-assembly.md` | topic | ⬜ |
| 5.7 | `docs/rag/rag-evaluation-and-metrics.md` | topic | ⬜ |
| 5.8 | `docs/rag/architecture.md` | architecture | ⬜ |
| 5.9 | `docs/rag/implementation-reference.md` | implementation-reference | ⬜ |
| 5.10 | `docs/rag/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 5.L1 | `labs/rag/README.md` | lab-readme | ⬜ |
| 5.L2 | `labs/rag/lab-embeddings/` | implementation | ⬜ |
| 5.L3 | `labs/rag/lab-chunking-strategies/` | implementation | ⬜ |
| 5.L4 | `labs/rag/lab-retrieval-playground/` | implementation | ⬜ |
| 5.L5 | `labs/rag/lab-query-pipeline/` | implementation | ⬜ |
| 5.L6 | `labs/rag/lab-rag-evaluation/` | implementation | ⬜ |

---

### 6. memory-context

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 6.1 | `docs/memory-context/README.md` | step-readme | ⬜ |
| 6.2 | `docs/memory-context/memory-types.md` | topic | ⬜ |
| 6.3 | `docs/memory-context/conversation-history.md` | topic | ⬜ |
| 6.4 | `docs/memory-context/context-management.md` | topic | ⬜ |
| 6.5 | `docs/memory-context/external-memory.md` | topic | ⬜ |
| 6.6 | `docs/memory-context/architecture.md` | architecture | ⬜ |
| 6.7 | `docs/memory-context/implementation-reference.md` | implementation-reference | ⬜ |
| 6.8 | `docs/memory-context/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 6.L1 | `labs/memory-context/README.md` | lab-readme | ⬜ |
| 6.L2 | `labs/memory-context/lab-memory-types/` | observation | ⬜ |
| 6.L3 | `labs/memory-context/lab-conversation-history/` | implementation | ⬜ |
| 6.L4 | `labs/memory-context/lab-context-management/` | implementation | ⬜ |
| 6.L5 | `labs/memory-context/lab-external-memory/` | implementation (optional) | ⬜ |

---

### 7. ai-agents

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 7.1 | `docs/ai-agents/README.md` | step-readme | ⬜ |
| 7.2 | `docs/ai-agents/agent-fundamentals.md` | topic | ⬜ |
| 7.3 | `docs/ai-agents/single-agent-loop.md` | topic | ⬜ |
| 7.4 | `docs/ai-agents/tool-use-loops.md` | topic | ⬜ |
| 7.5 | `docs/ai-agents/multi-agent-systems.md` | topic | ⬜ |
| 7.6 | `docs/ai-agents/agent-patterns.md` | topic | ⬜ |
| 7.7 | `docs/ai-agents/architecture.md` | architecture | ⬜ |
| 7.8 | `docs/ai-agents/implementation-reference.md` | implementation-reference | ⬜ |
| 7.9 | `docs/ai-agents/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 7.L1 | `labs/ai-agents/README.md` | lab-readme | ⬜ |
| 7.L2 | `labs/ai-agents/lab-single-agent-loop/` | implementation | ⬜ |
| 7.L3 | `labs/ai-agents/lab-tool-use-loops/` | implementation | ⬜ |
| 7.L4 | `labs/ai-agents/lab-multi-agent/` | integration | ⬜ |
| 7.L5 | `labs/ai-agents/lab-agent-patterns/` | implementation (optional) | ⬜ |

---

### 8. frameworks-tools

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 8.1 | `docs/frameworks-tools/README.md` | step-readme | ⬜ |
| 8.2 | `docs/frameworks-tools/langchain.md` | topic | ⬜ |
| 8.3 | `docs/frameworks-tools/llamaindex.md` | topic | ⬜ |
| 8.4 | `docs/frameworks-tools/autogen.md` | topic | ⬜ |
| 8.5 | `docs/frameworks-tools/semantic-kernel.md` | topic | ⬜ |
| 8.6 | `docs/frameworks-tools/framework-comparison.md` | topic | ⬜ |
| 8.7 | `docs/frameworks-tools/architecture.md` | architecture | ⬜ |
| 8.8 | `docs/frameworks-tools/implementation-reference.md` | implementation-reference | ⬜ |
| 8.9 | `docs/frameworks-tools/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 8.L1 | `labs/frameworks-tools/README.md` | lab-readme | ⬜ |
| 8.L2 | `labs/frameworks-tools/lab-langchain/` | implementation | ⬜ |
| 8.L3 | `labs/frameworks-tools/lab-llamaindex/` | implementation | ⬜ |
| 8.L4 | `labs/frameworks-tools/lab-autogen/` | implementation (optional) | ⬜ |
| 8.L5 | `labs/frameworks-tools/lab-semantic-kernel/` | implementation (optional) | ⬜ |

---

### 9. ai-java

**Docs** (no labs for this module)

| # | File | Type | Status |
|---|------|------|--------|
| 9.1 | `docs/ai-java/README.md` | step-readme | ⬜ |
| 9.2 | `docs/ai-java/java-ai-landscape.md` | topic | ⬜ |
| 9.3 | `docs/ai-java/spring-ai.md` | topic | ⬜ |
| 9.4 | `docs/ai-java/langchain4j.md` | topic | ⬜ |
| 9.5 | `docs/ai-java/java-patterns.md` | topic | ⬜ |
| 9.6 | `docs/ai-java/architecture.md` | architecture | ⬜ |
| 9.7 | `docs/ai-java/implementation-reference.md` | implementation-reference | ⬜ |
| 9.8 | `docs/ai-java/validation.md` | validation | ⬜ |
| 9.L1 | `labs/ai-java/README.md` | lab-readme (no-labs note) | ⬜ |

---

## Phase 3 — Advanced modules

### 10. evaluation-testing

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 10.1 | `docs/evaluation-testing/README.md` | step-readme | ⬜ |
| 10.2 | `docs/evaluation-testing/evaluation-fundamentals.md` | topic | ⬜ |
| 10.3 | `docs/evaluation-testing/llm-evaluation-metrics.md` | topic | ⬜ |
| 10.4 | `docs/evaluation-testing/application-testing.md` | topic | ⬜ |
| 10.5 | `docs/evaluation-testing/mocking-and-integration.md` | topic | ⬜ |
| 10.6 | `docs/evaluation-testing/contract-testing.md` | topic | ⬜ |
| 10.7 | `docs/evaluation-testing/architecture.md` | architecture | ⬜ |
| 10.8 | `docs/evaluation-testing/implementation-reference.md` | implementation-reference | ⬜ |
| 10.9 | `docs/evaluation-testing/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 10.L1 | `labs/evaluation-testing/README.md` | lab-readme | ⬜ |
| 10.L2 | `labs/evaluation-testing/lab-evaluation-metrics/` | implementation | ⬜ |
| 10.L3 | `labs/evaluation-testing/lab-application-testing/` | implementation | ⬜ |
| 10.L4 | `labs/evaluation-testing/lab-mocking/` | implementation | ⬜ |
| 10.L5 | `labs/evaluation-testing/lab-contract-testing/` | implementation (optional) | ⬜ |

---

### 11. safety-guardrails

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 11.1 | `docs/safety-guardrails/README.md` | step-readme | ⬜ |
| 11.2 | `docs/safety-guardrails/safety-fundamentals.md` | topic | ⬜ |
| 11.3 | `docs/safety-guardrails/input-guardrails.md` | topic | ⬜ |
| 11.4 | `docs/safety-guardrails/output-guardrails.md` | topic | ⬜ |
| 11.5 | `docs/safety-guardrails/vulnerabilities.md` | topic | ⬜ |
| 11.6 | `docs/safety-guardrails/red-teaming.md` | topic | ⬜ |
| 11.7 | `docs/safety-guardrails/architecture.md` | architecture | ⬜ |
| 11.8 | `docs/safety-guardrails/implementation-reference.md` | implementation-reference | ⬜ |
| 11.9 | `docs/safety-guardrails/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 11.L1 | `labs/safety-guardrails/README.md` | lab-readme | ⬜ |
| 11.L2 | `labs/safety-guardrails/lab-input-guardrails/` | implementation | ⬜ |
| 11.L3 | `labs/safety-guardrails/lab-output-guardrails/` | implementation | ⬜ |
| 11.L4 | `labs/safety-guardrails/lab-red-teaming/` | observation + implementation | ⬜ |

---

### 12. performance-optimization

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 12.1 | `docs/performance-optimization/README.md` | step-readme | ⬜ |
| 12.2 | `docs/performance-optimization/latency-and-throughput.md` | topic | ⬜ |
| 12.3 | `docs/performance-optimization/caching-strategies.md` | topic | ⬜ |
| 12.4 | `docs/performance-optimization/prompt-optimization.md` | topic | ⬜ |
| 12.5 | `docs/performance-optimization/model-selection.md` | topic | ⬜ |
| 12.6 | `docs/performance-optimization/batching.md` | topic | ⬜ |
| 12.7 | `docs/performance-optimization/architecture.md` | architecture | ⬜ |
| 12.8 | `docs/performance-optimization/implementation-reference.md` | implementation-reference | ⬜ |
| 12.9 | `docs/performance-optimization/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 12.L1 | `labs/performance-optimization/README.md` | lab-readme | ⬜ |
| 12.L2 | `labs/performance-optimization/lab-latency-benchmarks/` | observation | ⬜ |
| 12.L3 | `labs/performance-optimization/lab-caching/` | implementation | ⬜ |
| 12.L4 | `labs/performance-optimization/lab-prompt-optimization/` | implementation | ⬜ |
| 12.L5 | `labs/performance-optimization/lab-batching/` | implementation (optional) | ⬜ |

---

### 13. deployment-scaling

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 13.1 | `docs/deployment-scaling/README.md` | step-readme | ⬜ |
| 13.2 | `docs/deployment-scaling/deployment-patterns.md` | topic | ⬜ |
| 13.3 | `docs/deployment-scaling/containerization.md` | topic | ⬜ |
| 13.4 | `docs/deployment-scaling/api-gateway.md` | topic | ⬜ |
| 13.5 | `docs/deployment-scaling/scaling-strategies.md` | topic | ⬜ |
| 13.6 | `docs/deployment-scaling/infrastructure-as-code.md` | topic | ⬜ |
| 13.7 | `docs/deployment-scaling/architecture.md` | architecture | ⬜ |
| 13.8 | `docs/deployment-scaling/implementation-reference.md` | implementation-reference | ⬜ |
| 13.9 | `docs/deployment-scaling/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 13.L1 | `labs/deployment-scaling/README.md` | lab-readme | ⬜ |
| 13.L2 | `labs/deployment-scaling/lab-containerization/` | implementation | ⬜ |
| 13.L3 | `labs/deployment-scaling/lab-api-gateway/` | implementation | ⬜ |
| 13.L4 | `labs/deployment-scaling/lab-scaling/` | implementation (optional) | ⬜ |
| 13.L5 | `labs/deployment-scaling/lab-iac/` | implementation (optional) | ⬜ |

---

### 14. observability-mlops

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 14.1 | `docs/observability-mlops/README.md` | step-readme | ⬜ |
| 14.2 | `docs/observability-mlops/observability-fundamentals.md` | topic | ⬜ |
| 14.3 | `docs/observability-mlops/tracing-and-logging.md` | topic | ⬜ |
| 14.4 | `docs/observability-mlops/prompt-versioning.md` | topic | ⬜ |
| 14.5 | `docs/observability-mlops/continuous-evaluation.md` | topic | ⬜ |
| 14.6 | `docs/observability-mlops/mlops-patterns.md` | topic | ⬜ |
| 14.7 | `docs/observability-mlops/architecture.md` | architecture | ⬜ |
| 14.8 | `docs/observability-mlops/implementation-reference.md` | implementation-reference | ⬜ |
| 14.9 | `docs/observability-mlops/validation.md` | validation | ⬜ |

**Labs**

| # | File | Lab | Status |
|---|------|-----|--------|
| 14.L1 | `labs/observability-mlops/README.md` | lab-readme | ⬜ |
| 14.L2 | `labs/observability-mlops/lab-tracing/` | implementation | ⬜ |
| 14.L3 | `labs/observability-mlops/lab-prompt-versioning/` | implementation | ⬜ |
| 14.L4 | `labs/observability-mlops/lab-continuous-eval/` | implementation | ⬜ |

---

### 15. reference-architectures

**Docs** (all concept-only, no labs)

| # | File | Type | Status |
|---|------|------|--------|
| 15.1 | `docs/reference-architectures/README.md` | step-readme | ⬜ |
| 15.2 | `docs/reference-architectures/pattern-map.md` | topic | ⬜ |
| 15.3 | `docs/reference-architectures/rag-system.md` | reference-architecture | ⬜ |
| 15.4 | `docs/reference-architectures/agent-system.md` | reference-architecture | ⬜ |
| 15.5 | `docs/reference-architectures/multi-agent-platform.md` | reference-architecture | ⬜ |
| 15.6 | `docs/reference-architectures/production-llm-api.md` | reference-architecture | ⬜ |
| 15.7 | `docs/reference-architectures/validation.md` | validation | ⬜ |

---

### 16. real-world-projects

**Docs**

| # | File | Type | Status |
|---|------|------|--------|
| 16.1 | `docs/real-world-projects/README.md` | step-readme | ⬜ |
| 16.2 | `docs/real-world-projects/validation.md` | validation | ⬜ |

**Labs** (full projects)

| # | File | Description | Status |
|---|------|-------------|--------|
| 16.L1 | `labs/real-world-projects/rag-assistant/` | End-to-end RAG app (Python) | ⬜ |
| 16.L2 | `labs/real-world-projects/agent-workflow/` | Multi-tool agent system (Python) | ⬜ |
| 16.L3 | `labs/real-world-projects/java-rag-assistant/` | RAG variant with Spring AI (Java) | ⬜ |

---

## Cross-module

| # | File | Status |
|---|------|--------|
| X.1 | `docs/reference/glossary.md` | ⬜ |

Populated incrementally as modules are written. Never written in one pass.

---

## Totals

| Category | Count |
|----------|-------|
| Doc files (all types) | 141 |
| Lab folders | 57 |
| Total work units | 198 |

---

## Last updated

Session: Fase 2 — meta/ setup (continued)
Date: 2026-04-15
