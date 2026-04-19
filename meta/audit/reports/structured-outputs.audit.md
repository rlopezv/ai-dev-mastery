# structured-outputs — Audit Report

**Module:** `structured-outputs`
**Level:** intermediate
**Audit date:** 2026-04-18
**Auditor:** Claude Sonnet 4.6 (static) / pending (execution)
**Branch:** `retrofit/editorial-reform`

---

## Scope

| Area | Files audited |
|------|--------------|
| Docs | `README.md`, `structured-outputs.md`, `tool-usage.md`, `tool-patterns.md`, `schema-design.md`, `architecture.md`, `implementation-reference.md`, `validation.md` |
| Labs | `labs/structured-outputs/README.md`, `lab-structured-outputs/README.md`, `lab-tool-usage/README.md`, `lab-tool-patterns/README.md`, `lab-schema-design/README.md` |
| main.py | `lab-structured-outputs`, `lab-tool-usage`, `lab-tool-patterns`, `lab-schema-design` |

---

## Static Checks

### Docs — Structural Compliance

| Check | Status | Notes |
|-------|--------|-------|
| SC-1 Frontmatter present and valid | PASS | All 8 docs have complete, valid frontmatter |
| SC-3 Navigation breadcrumb present | PASS | All docs have `## Navigation` |
| SC-4 No placeholders | PASS | No TBD/TODO/... found |
| SC-6 H1 matches frontmatter title | PASS | All H1s match |
| IQ-3 Cross-references resolve | PASS | All `prerequisites`, `related`, `next` point to existing files |
| IQ-6 Concepts in glossary | PASS | All frontmatter concepts verified after fixes |

### Docs — Content Quality (static)

| Check | Status | Notes |
|-------|--------|-------|
| SC-2 Document type matches structure | PASS | All types correctly applied |
| CQ-2 Explanations are causal | PASS | Why/How/Code pattern followed in all topics |
| CQ-4 Terminology consistent | PASS | No naming variants found within docs after fixes |
| EQ-1 Engineering implications explicit | PASS | Each topic has dedicated Engineering Implications section |
| LC-1 Runtime complexity matches level | PASS | Intermediate module using foundational infrastructure profile (Ollama + SDK, no vector DB) — valid per LEVEL_MODE |

### Labs — Structural

| Check | Status | Notes |
|-------|--------|-------|
| LS-7 Frontmatter present and valid | PASS | All 4 individual lab READMEs have frontmatter after fixes |
| LS-8 H1 matches title | PASS | All H1s match |
| LS-1 Navigation breadcrumb present | PASS | All lab READMEs have `## Navigation` |
| LS-4 main.py exists | PASS | All 4 individual labs have `main.py` |
| DA-4 README sections match scaffold | PASS | All 4 lab READMEs restructured to scaffold after fixes |
| DA-3 Concept names match glossary | PASS | Fixed: see Fixes applied section |

### Checks Not Applied in This Pass

The following checks from `meta/standards/validation/docs-checklist.md` were not applied in this static-only pass. They are deferred to the cohesion audit (`/audit-module`).

| Check | Result | Notes |
|-------|--------|-------|
| SC-5 Tables present where required | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-1 Concepts technically correct | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-3 Coverage complete | SKIP | Not applied in this pass — deferred to cohesion audit |
| CQ-5 Limitations acknowledged | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-1 Explanation progressive | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-2 Reader assumptions appropriate | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-3 Mental models clear | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-4 Examples meaningful | SKIP | Not applied in this pass — deferred to cohesion audit |
| PQ-5 Tables reduce cognitive load | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-2 Trade-offs identified | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-3 Real system behavior reflected | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-4 Abstract explanation grounded | SKIP | Not applied in this pass — deferred to cohesion audit |
| EQ-5 Operational risks mentioned | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-1 Sandbox alignment | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-2 Cross-references meaningful | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-4 Validation references present | SKIP | Not applied in this pass — deferred to cohesion audit |
| IQ-5 Fits roadmap position | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-2 Components justified | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-3 Abstraction level appropriate | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-4 Observability requirements addressed | SKIP | Not applied in this pass — deferred to cohesion audit |
| LC-5 Level exceptions documented | SKIP | Not applied in this pass — deferred to cohesion audit |

---

## Fixes Applied During Audit

| File | Fix |
|------|-----|
| `docs/structured-outputs/implementation-reference.md` | `light` → `foundational` in External Dependencies table (4 rows: Ollama, openai SDK, pydantic, anthropic SDK) |
| `docs/reference/glossary.md` | Added `### schema-design` (referenced by lab-schema-design but absent) |
| `docs/reference/glossary.md` | Added `### schema-enforcement` (referenced by lab-structured-outputs and lab-schema-design but absent) |
| `labs/structured-outputs/lab-structured-outputs/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section; fixed concept: `"structured-outputs"` → `"structured-output"` |
| `labs/structured-outputs/lab-tool-usage/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section |
| `labs/structured-outputs/lab-tool-patterns/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section; fixed concepts: `"parallel-tool-calls"` → `"parallel-tools"`, `"sequential-tool-calls"` → `"sequential-chain"` |
| `labs/structured-outputs/lab-schema-design/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section |

---

## Execution Checks

Checks that require running the labs against a live Ollama instance.

| Check | Status | What to verify |
|-------|--------|---------------|
| EV-1 Lab runs without error | PENDING | `python lab-structured-outputs/main.py` exits 0 |
| EV-1 Lab runs without error | PENDING | `python lab-tool-usage/main.py` exits 0 |
| EV-1 Lab runs without error | PENDING | `python lab-tool-patterns/main.py` exits 0 |
| EV-1 Lab runs without error | PENDING | `python lab-schema-design/main.py` exits 0 (optional lab) |
| EV-2 Environment reproducible | PENDING | `requirements.txt` installs cleanly; Ollama + `llama3.2` setup works |
| EV-3 Dependencies resolved | PENDING | `openai>=1.40.0`, `pydantic>=2.0.0`, `anthropic`, `python-dotenv` importable |
| BC-1 Expected outputs correct | PENDING | `message.parsed` returns typed object; `finish_reason` is `"tool_calls"` on first tool call response; parallel pattern shows `len(msg.tool_calls) >= 2` |
| BC-2 System behaves as described | PENDING | Schema enforcement parse success 5/5; prompt-only fails on adversarial inputs; sequential chain round-trips = 3 |
| BC-5 Outputs deterministic enough | PENDING | Router pattern selects correct tool for all 4 query types |

---

## Overall Status

| Dimension | Status |
|-----------|--------|
| Static checks | PASS |
| Execution checks | PENDING |
| **Module** | **STATIC_PASS / EXECUTION_PENDING** |

Module is not **FULL_PASS** until execution checks are completed against a running Ollama instance with `llama3.2` loaded and valid `ANTHROPIC_API_KEY` for Observation 3 of `lab-tool-usage`.
