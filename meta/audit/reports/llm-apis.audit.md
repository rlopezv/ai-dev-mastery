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

## Static Checks

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

## Execution Checks

Checks that require running the labs against live Ollama or cloud API keys.

| Check | Status | What to verify |
|-------|--------|---------------|
| EV-1 Lab runs without error | PENDING | `python lab-openai-api/main.py` exits 0 (requires `OPENAI_API_KEY`) |
| EV-1 Lab runs without error | PENDING | `python lab-anthropic-api/main.py` exits 0 (requires `ANTHROPIC_API_KEY`) |
| EV-1 Lab runs without error | PENDING | `python lab-ollama-api/main.py` exits 0 (requires `ollama serve` + `llama3.2`) |
| EV-1 Lab runs without error | PENDING | `python lab-streaming/main.py` exits 0 (requires `ollama serve` + `llama3.2`) |
| EV-1 Lab runs without error | PENDING | `python lab-api-patterns/main.py` exits 0 (Ollama required; Anthropic optional) |
| EV-2 Environment reproducible | PENDING | `requirements.txt` installs cleanly; `.env.example` → `.env` workflow works |
| EV-3 Dependencies resolved | PENDING | `openai`, `anthropic`, `python-dotenv` importable after `pip install -r requirements.txt` |
| BC-1 Expected outputs correct | PENDING | `finish_reason` present; `prompt_tokens` grows across turns; streaming prints tokens progressively |
| BC-2 System behaves as described | PENDING | `finish_reason="length"` triggers warning; retry doubles delay; `ChatResponse` normalizes both providers |
| BC-5 Outputs deterministic enough | PENDING | Schema diff table stable; `stop_reason` normalization consistent across runs |

---

## Overall Status

| Dimension | Status |
|-----------|--------|
| Static checks | PASS |
| Execution checks | PENDING |
| **Module** | **STATIC_PASS / EXECUTION_PENDING** |

Module is not **FULL_PASS** until execution checks are completed against a running Ollama instance (`llama3.2`) with valid `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.
