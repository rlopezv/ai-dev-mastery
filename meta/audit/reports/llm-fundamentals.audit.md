# llm-fundamentals — Audit Report

**Module:** `llm-fundamentals`
**Level:** foundational
**Audit date:** 2026-04-18
**Auditor:** Claude Sonnet 4.6 (static) / pending (execution)
**Branch:** `retrofit/editorial-reform`

---

## Scope

| Area | Files audited |
|------|--------------|
| Docs | `README.md`, `llm-architecture.md`, `tokenization.md`, `context-window.md`, `inference-parameters.md`, `fine-tuning.md`, `multimodality.md`, `architecture.md`, `implementation-reference.md`, `validation.md` |
| Labs | `labs/llm-fundamentals/README.md`, `lab-llm-anatomy/README.md`, `lab-tokenization/README.md`, `lab-context-window/README.md`, `lab-inference-parameters/README.md` |
| main.py | `lab-llm-anatomy`, `lab-tokenization`, `lab-context-window`, `lab-inference-parameters` |

---

## Phase 1 — Static

Covers structural and alignment checks verifiable without executing the labs or reading content for correctness.

### Docs — Structural Compliance

| Check | Status | Notes |
|-------|--------|-------|
| SC-1 Frontmatter present and valid | PASS | All 10 docs have complete, valid frontmatter |
| SC-3 Navigation breadcrumb present | PASS | All docs have `## Navigation` |
| SC-4 No placeholders | PASS | No TBD/TODO/... found |
| SC-6 H1 matches frontmatter title | PASS | All H1s match |
| IQ-3 Cross-references resolve | PASS | All `prerequisites`, `related`, `next` point to existing files |
| IQ-6 Concepts in glossary | PASS | All frontmatter concepts verified against `docs/reference/glossary.md` |

### Docs — Content Quality (static)

| Check | Status | Notes |
|-------|--------|-------|
| SC-2 Document type matches structure | PASS | All types correctly applied |
| CQ-2 Explanations are causal | PASS | Why/How/Code pattern followed in all topics |
| CQ-4 Terminology consistent | PASS | No naming variants found within docs |
| EQ-1 Engineering implications explicit | PASS | Each topic has dedicated Engineering Implications section |
| LC-1 Runtime complexity matches level | PASS | Foundational profile — Ollama only, no vector DB |

### Labs — Structural

| Check | Status | Notes |
|-------|--------|-------|
| LS-7 Frontmatter present and valid | PASS | All 5 lab READMEs have frontmatter |
| LS-8 H1 matches title | PASS | All H1s match after fix |
| LS-1 Navigation breadcrumb present | PASS | All lab READMEs have `## Navigation` |
| LS-4 main.py exists | PASS | All 4 individual labs have `main.py` |
| DA-4 README sections match scaffold | PASS | All 4 lab READMEs restructured to scaffold order after fix |
| DA-3 Concept names match glossary | PASS | Fixed: `top-k`→`top-k-sampling`, `top-p`→`top-p-sampling` |

### Fixes applied during audit

| File | Fix |
|------|-----|
| `docs/llm-fundamentals/llm-architecture.md` | `light` → `foundational` in Implementation Connection |
| `docs/llm-fundamentals/context-window.md` | `light` → `foundational` in Implementation Connection |
| `docs/llm-fundamentals/implementation-reference.md` | `light` → `foundational` in External Dependencies table (2 rows) |
| `labs/llm-fundamentals/lab-llm-anatomy/README.md` | Restructured to scaffold; added Concepts table; Infrastructure section |
| `labs/llm-fundamentals/lab-tokenization/README.md` | Restructured to scaffold; added Concepts table; Spanish added to Observation 2 |
| `labs/llm-fundamentals/lab-context-window/README.md` | Restructured to scaffold; added Concepts table; Infrastructure section |
| `labs/llm-fundamentals/lab-inference-parameters/README.md` | Restructured to scaffold; added Observation 4 (top_p); fixed concept names in frontmatter |

### Checks Not Applied in This Pass

The following checks from `meta/standards/validation/docs-checklist.md` were not applied in this static-only pass. They are deferred to the cohesion audit (`/audit-module`).

| Check | Result | Notes |
|-------|--------|-------|
| SC-5 Tables present where required | PENDING | Deferred to cohesion audit |
| CQ-1 Concepts technically correct | PENDING | Deferred to cohesion audit |
| CQ-3 Coverage complete | PENDING | Deferred to cohesion audit |
| CQ-5 Limitations acknowledged | PENDING | Deferred to cohesion audit |
| PQ-1 Explanation progressive | PENDING | Deferred to cohesion audit |
| PQ-2 Reader assumptions appropriate | PENDING | Deferred to cohesion audit |
| PQ-3 Mental models clear | PENDING | Deferred to cohesion audit |
| PQ-4 Examples meaningful | PENDING | Deferred to cohesion audit |
| PQ-5 Tables reduce cognitive load | PENDING | Deferred to cohesion audit |
| EQ-2 Trade-offs identified | PENDING | Deferred to cohesion audit |
| EQ-3 Real system behavior reflected | PENDING | Deferred to cohesion audit |
| EQ-4 Abstract explanation grounded | PENDING | Deferred to cohesion audit |
| EQ-5 Operational risks mentioned | PENDING | Deferred to cohesion audit |
| IQ-1 Sandbox alignment | PENDING | Deferred to cohesion audit |
| IQ-2 Cross-references meaningful | PENDING | Deferred to cohesion audit |
| IQ-4 Validation references present | PENDING | Deferred to cohesion audit |
| IQ-5 Fits roadmap position | PENDING | Deferred to cohesion audit |
| LC-2 Components justified | PENDING | Deferred to cohesion audit |
| LC-3 Abstraction level appropriate | PENDING | Deferred to cohesion audit |
| LC-4 Observability requirements addressed | PENDING | Deferred to cohesion audit |
| LC-5 Level exceptions documented | PENDING | Deferred to cohesion audit |

---

## Phase 2 — Cohesion

Covers content correctness, pedagogical quality, engineering quality, integration quality, and level compliance. Applied to all 10 docs.

**Audit date:** 2026-04-19
**Auditor:** Claude Sonnet 4.6

### Cohesion checks — all docs

| Check | Status | Notes |
|-------|--------|-------|
| CQ-1 Concepts technically correct | PASS | All topics: transformer, BPE, attention, autoregressive loop, inference parameters, LoRA, vision encoder — technically accurate throughout |
| CQ-2 Explanations causal | PASS | Already confirmed in Phase 1 |
| CQ-3 Coverage complete | PASS | Every doc fulfills its declared scope; all frontmatter `concepts` fields fully covered |
| CQ-4 Terminology consistent | PASS | Already confirmed in Phase 1 |
| CQ-5 Limitations acknowledged | PASS | Every topic and architecture doc has a dedicated Failure Modes / Limitations section |
| PQ-1 Explanation progressive | PASS | Intuition → Why → How → Engineering → Failure modes in all topic docs |
| PQ-2 Reader assumptions appropriate | PASS | No deep ML assumed; analogies (RAM buffer, codec, biased coin flip) appropriate for Java architects |
| PQ-3 Mental models clear | PASS | Concept map in README, component diagrams in architecture.md, analogy-per-topic pattern consistent |
| PQ-4 Examples meaningful | PASS | Code examples reference concrete labs; decision tables are actionable |
| PQ-5 Tables reduce cognitive load | PASS | Synthesis tables used for component breakdowns, parameter references, lab mappings |
| EQ-1 Engineering implications explicit | PASS | Already confirmed in Phase 1 |
| EQ-2 Trade-offs identified | PASS | Temperature/diversity, context cost, fine-tuning maintenance burden, resolution/token trade-offs |
| EQ-3 Real system behavior reflected | PASS | Ollama API fields (`prompt_eval_count`, `eval_count`), tiktoken encoding, provider-specific limits referenced throughout |
| EQ-4 Abstract explanation grounded | PASS | All abstractions anchored to concrete tool interfaces or observable behaviors |
| EQ-5 Operational risks mentioned | PASS | Silent truncation, hallucination, tokenizer mismatch, parameter interaction, data contamination — all covered |
| IQ-1 Sandbox alignment | PASS | Foundational profile (Ollama only) consistent across all docs; concept-only topics correctly declare no runtime requirement |
| IQ-2 Cross-references meaningful | PASS | Inter-module references (RAG, memory-context, agents) correctly motivated by the concept being covered |
| IQ-3 Implementation references concrete | PASS | Already confirmed in Phase 1 |
| IQ-4 Validation references present | PASS | All docs reference `docs-checklist.md`; validation.md also references `labs-checklist.md` |
| IQ-5 Fits roadmap position | PASS | Already confirmed in Phase 1 |
| LC-2 Components justified | PASS | Ollama, tiktoken, and requests justified by pedagogical role in each doc |
| LC-3 Abstraction level appropriate | PASS | Raw APIs throughout; no framework wrappers introduced |
| LC-4 Observability requirements addressed | PASS | Labs map directly to pipeline components; observables (token counts, variance, budget arithmetic) explicitly stated |
| LC-5 Level exceptions documented | PASS | No exceptions from foundational profile; concept-only topics (fine-tuning, multimodality) explicitly state no lab |
| SC-5 Tables present where required | PASS | All docs include required synthesis/comparison tables |

### Fixes applied during Phase 2

None required. All 10 documents passed all cohesion checks.

### Frontmatter sync

`python .work/scripts/sync-frontmatter-status.py llm-fundamentals final` — 10 files updated `draft → final`. No WARN lines.

> **Script bug fixed:** The script was not updating files because `status` values use YAML quoted strings (`"draft"`) but the comparison list had unquoted strings. Fixed by stripping quotes in `sync_status()`.

---

## Phase 3 — Execution

Checks that require running the labs against a live Ollama instance.

| Check | Status | What to verify |
|-------|--------|---------------|
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-llm-anatomy/main.py` exits 0 |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-tokenization/main.py` exits 0 |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-context-window/main.py` exits 0 |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-inference-parameters/main.py` exits 0 |
| EV-2 Environment reproducible | PENDING | Requires live infrastructure — `requirements.txt` installs cleanly; Ollama setup works per README |
| EV-3 Dependencies resolved | PENDING | Requires live infrastructure — `tiktoken`, `requests` importable after `pip install -r requirements.txt` |
| BC-1 Expected outputs correct | PENDING | Requires live infrastructure — `prompt_eval_count` stable across runs; `eval_count` bounded by `num_predict` |
| BC-2 System behaves as described | PENDING | Requires live infrastructure — temperature=0 produces identical output; temperature=1.0 produces variance |
| BC-5 Outputs deterministic enough | PENDING | Requires live infrastructure — Observation assertions match README expected output within described bounds |

---

## Overall Status

| Dimension | Status |
|-----------|--------|
| Static checks | PASS |
| Cohesion checks | PASS |
| Execution checks | PENDING |
| **Module** | **STATIC_PASS \| COHESION_PASS \| EXECUTION_PENDING** |

Module is not **FULL_PASS** until execution checks are completed against a running Ollama instance with `llama3.2` loaded.
