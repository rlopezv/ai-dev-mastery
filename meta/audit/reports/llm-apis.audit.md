# llm-apis — Audit Report

**Module:** `llm-apis`
**Level:** foundational
**Audit date:** 2026-04-18
**Auditor:** Claude Sonnet 4.6 (static) / pending (execution)
**Branch:** `retrofit/editorial-reform`

---

## Scope

| Area | Files audited |
|------|--------------|
| Docs | `README.md`, `openai-api.md`, `anthropic-api.md`, `ollama-api.md`, `api-patterns.md`, `streaming.md`, `architecture.md`, `implementation-reference.md`, `validation.md` |
| Labs | `labs/llm-apis/README.md`, `lab-openai-api/README.md`, `lab-anthropic-api/README.md`, `lab-ollama-api/README.md`, `lab-streaming/README.md`, `lab-api-patterns/README.md` |
| main.py | `lab-openai-api`, `lab-anthropic-api`, `lab-ollama-api`, `lab-streaming`, `lab-api-patterns` |

---

## Phase 1 — Static

### Docs — Structural Compliance

| Check | Status | Notes |
|-------|--------|-------|
| SC-1 Frontmatter present and valid | PASS | All 9 docs have complete, valid frontmatter |
| SC-3 Navigation breadcrumb present | PASS | All docs have `## Navigation` |
| SC-4 No placeholders | PASS | No TBD/TODO/... found |
| SC-6 H1 matches frontmatter title | PASS | All H1s match |
| IQ-3 Cross-references resolve | PASS | All `prerequisites`, `related`, `next` point to existing files |
| IQ-6 Concepts in glossary | PASS | All frontmatter concepts verified; `finish-reason` added to glossary during audit |

### Docs — Content Quality (static)

| Check | Status | Notes |
|-------|--------|-------|
| SC-2 Document type matches structure | PASS | All types correctly applied |
| CQ-2 Explanations are causal | PASS | Why/How/Code pattern followed in all topics |
| CQ-4 Terminology consistent | PASS | No naming variants found within docs after fixes |
| EQ-1 Engineering implications explicit | PASS | Each topic has dedicated Engineering Implications section |
| LC-1 Runtime complexity matches level | PASS | Foundational profile — Ollama + cloud API keys, no Docker/vector DB |

### Labs — Structural

| Check | Status | Notes |
|-------|--------|-------|
| LS-7 Frontmatter present and valid | PASS | All 5 individual lab READMEs have frontmatter after fixes |
| LS-8 H1 matches title | PASS | All H1s match |
| LS-1 Navigation breadcrumb present | PASS | All lab READMEs have `## Navigation` |
| LS-4 main.py exists | PASS | All 5 individual labs have `main.py` |
| DA-4 README sections match scaffold | PASS | All 5 lab READMEs restructured to scaffold order after fixes |
| DA-3 Concept names match glossary | PASS | Fixed: see Fixes applied section |

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

## Fixes Applied During Audit

| File | Fix |
|------|-----|
| `docs/llm-apis/implementation-reference.md` | `light` → `foundational` in External Dependencies table (3 rows) |
| `docs/llm-apis/ollama-api.md` | Removed `docker-compose.yml` / `ollama-init` references (inconsistent with foundational profile — Ollama runs directly, not via Docker) |
| `docs/reference/glossary.md` | Added `### finish reason` entry (referenced by lab-openai-api and lab-anthropic-api but absent) |
| `labs/llm-apis/lab-openai-api/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section; fixed concepts: `"chat-completions"` → `"chat-completion-api"`, `"message-roles"` → `"message-role"` |
| `labs/llm-apis/lab-anthropic-api/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section; fixed concept: `"message-roles"` → `"message-role"` |
| `labs/llm-apis/lab-ollama-api/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section; fixed concepts: `"openai-compatible-interface"` → `"openai-compatible-api"`, `"local-inference"` → `"local-llm-runtime"` |
| `labs/llm-apis/lab-streaming/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section |
| `labs/llm-apis/lab-api-patterns/README.md` | Restructured to scaffold; added Concepts table and Infrastructure section |

---

## Phase 3 — Execution

Checks that require running the labs against live Ollama or cloud API keys.

| Check | Status | What to verify |
|-------|--------|---------------|
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-openai-api/main.py` exits 0 (requires `OPENAI_API_KEY`) |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-anthropic-api/main.py` exits 0 (requires `ANTHROPIC_API_KEY`) |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-ollama-api/main.py` exits 0 (requires `ollama serve` + `llama3.2`) |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-streaming/main.py` exits 0 (requires `ollama serve` + `llama3.2`) |
| EV-1 Lab runs without error | PENDING | Requires live infrastructure — `python lab-api-patterns/main.py` exits 0 (Ollama required; Anthropic optional) |
| EV-2 Environment reproducible | PENDING | Requires live infrastructure — `requirements.txt` installs cleanly; `.env.example` → `.env` workflow works |
| EV-3 Dependencies resolved | PENDING | Requires live infrastructure — `openai`, `anthropic`, `python-dotenv` importable after `pip install -r requirements.txt` |
| BC-1 Expected outputs correct | PENDING | Requires live infrastructure — `finish_reason` present; `prompt_tokens` grows across turns; streaming prints tokens progressively |
| BC-2 System behaves as described | PENDING | Requires live infrastructure — `finish_reason="length"` triggers warning; retry doubles delay; `ChatResponse` normalizes both providers |
| BC-5 Outputs deterministic enough | PENDING | Requires live infrastructure — Schema diff table stable; `stop_reason` normalization consistent across runs |

---

## Overall Status

| Dimension | Status |
|-----------|--------|
| Static checks | PASS |
| Execution checks | PENDING |
| **Module** | **STATIC_PASS | COHESION_PENDING | EXECUTION_PENDING** |

Module is not **FULL_PASS** until execution checks are completed against a running Ollama instance (`llama3.2`) with valid `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.
