# Audit Report: frameworks-tools

**Date:** 2026-04-19
**Branch:** retrofit/editorial-reform
**Auditor:** Claude Code

---

## Scope

| Category | Files |
|----------|-------|
| Docs | `docs/frameworks-tools/README.md`, `langchain.md`, `llamaindex.md`, `autogen.md`, `semantic-kernel.md`, `framework-comparison.md`, `workflow-tools.md`, `architecture.md`, `implementation-reference.md`, `validation.md` |
| Labs | `labs/frameworks-tools/README.md`, `lab-langchain/`, `lab-llamaindex/`, `lab-autogen/`, `lab-semantic-kernel/`, `lab-integration/` |
| Alignment | `meta/system-design/DOCS_LABS_MAP.md` §frameworks-tools |
| Glossary | `docs/reference/glossary.md` |

---

## Static Checks

### Structural Compliance

| Check | Result | Notes |
|-------|--------|-------|
| SC-1 Frontmatter valid | PASS | All 10 docs + 6 lab READMEs have valid YAML frontmatter |
| SC-2 Document type matches artifact | PASS | step-readme, topic×5, architecture, implementation-reference, validation — all correct |
| SC-3 Navigation breadcrumb present | PASS | All files include `## Navigation` post-frontmatter |
| SC-4 No placeholders | PASS | No TODO, TBD, or incomplete sections found |
| SC-5 Tables present where required | PASS | Lab inventory, framework comparison tables, concept tables all present |
| SC-6 H1 matches frontmatter title | PASS | All 10 docs verified with automated check |

### Integration Quality

| Check | Result | Notes |
|-------|--------|-------|
| IQ-5 Fits roadmap position | PASS | Position 8: builds on ai-agents (agent loop); covers LangChain, LlamaIndex, AutoGen, Semantic Kernel |
| IQ-6 Concepts in glossary | FIXED | 4 terms missing — added during audit (see Fixes section) |

### Lab Structure

| Check | Result | Notes |
|-------|--------|-------|
| All required sections present | PASS | All 5 labs have Overview, Concepts, Setup, Run, Expected Output, Failure case, Infrastructure |
| Lab optional/required alignment | PASS | `lab-autogen`, `lab-semantic-kernel`, `lab-integration` correctly optional; `lab-langchain`, `lab-llamaindex` required — matches DOCS_LABS_MAP |

### Checks Not Applied in This Pass

The following checks from `meta/standards/validation/docs-checklist.md` were not applied in this static-only pass. They are deferred to the cohesion audit (`/audit-module`).

| Check | Result | Notes |
|-------|--------|-------|
| CQ-1 Concepts technically correct | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-2 Explanations causal | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-3 Coverage complete | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-4 Terminology consistent | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-5 Limitations acknowledged | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-1 Explanation progressive | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-2 Reader assumptions appropriate | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-3 Mental models clear | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-4 Examples meaningful | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-5 Tables reduce cognitive load | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-1 Engineering implications explicit | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-2 Trade-offs identified | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-3 Real system behavior reflected | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-4 Abstract explanation grounded | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-5 Operational risks mentioned | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-1 Sandbox alignment | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-2 Cross-references meaningful | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-3 Implementation references concrete | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-4 Validation references present | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-1 Runtime complexity matches level | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-2 Components justified | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-3 Abstraction level appropriate | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-4 Observability requirements addressed | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-5 Level exceptions documented | SKIP | Not applied in this pass — deferred to cohesion audit |

---

## DOCS_LABS_MAP Alignment

| Doc | Lab | Type | Required | Present |
|-----|-----|------|----------|---------|
| `langchain.md` | `lab-langchain` | implementation | yes | ✓ |
| `llamaindex.md` | `lab-llamaindex` | implementation | yes | ✓ |
| `autogen.md` | `lab-autogen` | implementation | optional | ✓ |
| `semantic-kernel.md` | `lab-semantic-kernel` | implementation | optional | ✓ |
| `framework-comparison.md` | — | concept-only | none | ✓ |
| `workflow-tools.md` | — | concept-only | none | ✓ |
| `architecture.md` | `lab-integration` | module-integration | optional | ✓ |

All 2 required labs present. All 3 optional labs also present.

---

## Glossary Check (IQ-6)

| Concept (frontmatter) | Glossary entry | Status |
|-----------------------|----------------|--------|
| `LangChain` | `LangChain` | PASS |
| `LlamaIndex` | `LlamaIndex` | PASS |
| `AutoGen` | `AutoGen` | PASS |
| `Semantic Kernel` | `Semantic Kernel` | PASS |
| `framework abstraction` | `framework abstraction` | PASS |
| `framework selection` | `framework selection` | PASS |
| `framework trade-offs` | `framework trade-offs` | FIXED — added during audit |
| `pipeline composition` | `pipeline composition` | PASS |
| `LCEL` | `LCEL` | PASS |
| `chain` | `chain` | PASS |
| `LangChain memory` | `LangChain memory` | PASS |
| `LangChain agent` | `LangChain agent` | PASS |
| `runnable` | `runnable` | PASS |
| `ConversableAgent` | `ConversableAgent` | PASS |
| `GroupChat` | `GroupChat` | PASS |
| `human-in-the-loop` | `human-in-the-loop` | PASS |
| `agent conversation` | `agent conversation` | FIXED — added during audit |
| `index` | `index` | PASS |
| `node` | `node` | PASS |
| `query engine` | `query engine` | PASS |
| `node parser` | `node parser` | PASS |
| `retriever` | `retriever` | FIXED — added during audit |
| `kernel` | `kernel` | PASS |
| `plugin` | `plugin` | PASS |
| `planner` | `planner` | PASS |
| `semantic function` | `semantic function` | PASS |
| `native function` | `native function` | PASS |
| `AI workflow tool` | `AI workflow tool` | PASS |
| `visual pipeline builder` | `visual pipeline builder` | FIXED — added during audit |
| `abstraction ceiling` | `abstraction ceiling` | PASS |

---

## Cross-Reference Validation

| Reference | Exists |
|-----------|--------|
| All internal `docs/frameworks-tools/*.md` cross-refs | ✓ |
| `docs/ai-agents/multi-agent-systems.md` | ✓ |
| `docs/structured-outputs/tool-usage.md` | ✓ |
| `docs/rag/embeddings-and-vector-search.md` | ✓ |
| `docs/rag/document-processing-and-chunking.md` | ✓ |

---

## Fixes Applied During Audit

1. **Added `framework trade-offs`** — engineering tensions of adopting a framework (boilerplate reduction vs. debugging complexity, speed vs. abstraction ceiling risk).
2. **Added `agent conversation`** — AutoGen interaction model of structured message exchange between `ConversableAgent` instances.
3. **Added `retriever`** — LlamaIndex component that decouples retrieval strategy from synthesis.
4. **Added `visual pipeline builder`** — drag-and-drop interface within AI workflow tools for constructing pipelines without code.

---

## Execution Checks

| Check | Status | What to verify |
|-------|--------|----------------|
| EV-1 Labs run without error | PENDING | `python lab-langchain/main.py`, `lab-llamaindex/main.py`, `lab-autogen/main.py`, `lab-semantic-kernel/main.py`, `lab-integration/main.py` |
| EV-2 LCEL chain produces output | PENDING | `lab-langchain` — chain invocation returns non-empty response |
| EV-3 LlamaIndex query returns grounded answer | PENDING | `lab-llamaindex` — query engine answer cites source nodes |
| BC-1 AutoGen group chat terminates | PENDING | `lab-autogen` — conversation reaches termination condition, not infinite loop |
| BC-2 Semantic Kernel planner selects correct function | PENDING | `lab-semantic-kernel` — planner routes task to registered plugin function |
| BC-5 Integration lab composes multiple frameworks | PENDING | `lab-integration` — LangChain + LlamaIndex components compose without conflict |

---

## Overall Status

**STATIC_PASS | EXECUTION_PENDING**

- All static checks pass after 4 glossary additions.
- No critical failures found.
- All required labs present and aligned with DOCS_LABS_MAP.
- Optional labs (`lab-autogen`, `lab-semantic-kernel`, `lab-integration`) correctly marked in both map and labs README.
