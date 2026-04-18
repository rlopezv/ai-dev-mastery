# Audit Report — `rag` module

**Date:** 2026-04-18
**Branch:** `retrofit/editorial-reform`
**Auditor:** Claude Code (claude-sonnet-4-6)
**Level declared:** Intermediate

---

## Scope

### Docs audited
- `docs/rag/README.md`
- `docs/rag/rag-fundamentals.md`
- `docs/rag/embeddings-and-vector-search.md`
- `docs/rag/document-processing-and-chunking.md`
- `docs/rag/retrieval-strategies.md`
- `docs/rag/context-assembly.md`
- `docs/rag/rag-evaluation-and-metrics.md`
- `docs/rag/architecture.md`
- `docs/rag/implementation-reference.md`
- `docs/rag/validation.md`

### Labs audited
- `labs/rag/README.md`
- `labs/rag/lab-embeddings/README.md`
- `labs/rag/lab-chunking-strategies/README.md`
- `labs/rag/lab-retrieval-playground/README.md`
- `labs/rag/lab-query-pipeline/README.md`
- `labs/rag/lab-rag-evaluation/README.md`
- `labs/rag/shared/config.py`

### Supporting files checked
- `meta/system-design/DOCS_LABS_MAP.md`
- `meta/system-design/LEVEL_MODE.md`
- `docs/reference/glossary.md`

---

## Static Checks

### Docs

| File | SC | CQ | PQ | EQ | IQ | LC | Result |
|------|----|----|----|----|----|----|--------|
| `README.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `rag-fundamentals.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `embeddings-and-vector-search.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `document-processing-and-chunking.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `retrieval-strategies.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `context-assembly.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `rag-evaluation-and-metrics.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |
| `architecture.md` | PASS | PASS | PASS | PASS | **FAIL** (IQ-6) | PASS | ⚠️ FIXED |
| `implementation-reference.md` | PASS | PASS | PASS | PASS | **FAIL** (IQ-6) | PASS | ⚠️ FIXED |
| `validation.md` | PASS | PASS | PASS | PASS | PASS | PASS | ✅ PASS |

**Docs quality summary:** Content, pedagogy, engineering quality, and level compliance are strong across all 10 documents. Two IQ-6 failures fixed during audit.

### Labs

| File | LS | DA | EQ | LC | Result |
|------|----|----|----|----|--------|
| `README.md` | PASS | PASS | PASS | PASS | ✅ PASS |
| `lab-embeddings/README.md` | **FAIL** (DA-4) | PASS | PASS | PASS | ⚠️ FIXED |
| `lab-chunking-strategies/README.md` | **FAIL** (DA-4) | PASS | PASS | PASS | ⚠️ FIXED |
| `lab-retrieval-playground/README.md` | **FAIL** (DA-4) | PASS | PASS | PASS | ⚠️ FIXED |
| `lab-query-pipeline/README.md` | **FAIL** (DA-4) | PASS | PASS | PASS | ⚠️ FIXED |
| `lab-rag-evaluation/README.md` | **FAIL** (DA-4) | PASS | PASS | PASS | ⚠️ FIXED |
| `shared/config.py` | **FAIL** (LS-6) | — | — | — | ⚠️ FIXED |

**Execution checks (EV-1, EV-2, EV-3, BC-1, BC-2, BC-5):** PENDING — not run against live infrastructure.

### Docs↔Labs Alignment (DOCS_LABS_MAP.md)

| Mapping | Status | Notes |
|---------|--------|-------|
| `rag-fundamentals.md` → none | ✅ | concept-only, no lab needed |
| `embeddings-and-vector-search.md` → `lab-embeddings` | ✅ | lab exists |
| `document-processing-and-chunking.md` → `lab-chunking-strategies` | ✅ | lab exists |
| `retrieval-strategies.md` → `lab-retrieval-playground` | ✅ | lab exists |
| `context-assembly.md` → `lab-query-pipeline` | ✅ | lab exists |
| `rag-evaluation-and-metrics.md` → `lab-rag-evaluation` | ✅ | lab exists |
| `architecture.md` → `lab-integration` | ❌ | lab declared **required** in DOCS_LABS_MAP but does not exist |

### Frontmatter Cross-references

All `prerequisites`, `next`, and `related` paths in docs frontmatter point to files that exist or are expected to exist in the module sequence. No broken cross-references detected.

### Glossary Check (IQ-6 / DA-3)

**Pre-audit missing concepts:**

From `docs/rag/architecture.md`:
- `document-ingestion-pipeline` ❌
- `vector-store` ❌
- `query-pipeline` ❌
- `context-assembler` ❌
- `evaluation-harness` ❌

From `docs/rag/implementation-reference.md`:
- `ingestion-pipeline` ❌
- `chromadb-collection` ❌
- `bm25-index` ❌
- `rrf-merge` ❌
- `token-budget-guard` ❌

**Action taken:** All 10 entries added to `docs/reference/glossary.md` during audit.

---

## Fixes Applied During Audit

### 1. Glossary additions (10 entries)
**File:** `docs/reference/glossary.md`
**Added:** `bm25-index`, `chromadb-collection`, `chunking` (already present), `context-assembler`, `document-ingestion-pipeline`, `evaluation-harness`, `ingestion-pipeline`, `query-pipeline`, `rrf-merge`, `token-budget-guard`, `vector-store`

### 2. implementation-reference.md §6 scope violation
**File:** `docs/rag/implementation-reference.md`
**Issue:** Section 6 contained bash setup commands (`ollama pull`, `ollama serve`) and operational "must be running" language, violating CLAUDE.md §10 scope policy for implementation-reference docs.
**Fix:** Removed bash commands; retained architectural integration description (endpoints, client pattern, ChromaDB instantiation pattern, tiktoken approximation rationale). Added pointer to `labs/rag/README.md` for setup steps.

### 3. Lab READMEs — missing sections
**Files:** All 5 individual lab READMEs
**Issues per DA-4:**
- Heading `## What this lab demonstrates` → renamed to `## Overview` (scaffold-compliant)
- `## Concepts` table missing (mapping concept → where it appears in code)
- `## Infrastructure` table missing (services and purposes)
**Fix:** Added both sections to all 5 lab READMEs with lab-specific content.

### 4. shared/config.py — missing load_corpus()
**File:** `labs/rag/shared/config.py`
**Issue:** LS-6 requires `shared/config.py` to expose a `load_corpus()` function. Function was absent.
**Fix:** Added `load_corpus(corpus_dir=None)` returning `list[tuple[str, str]]` (filename, text pairs), scanning `*.md` and `*.txt` files from the corpus directory.

---

## Execution Checks

| Check | Status | What to verify |
|-------|--------|----------------|
| EV-1 All labs run without error | PENDING | `python lab-*/main.py` in order |
| EV-2 Environment reproducible via documented steps | PENDING | Fresh devcontainer run |
| EV-3 Dependencies resolve from requirements.txt | PENDING | `pip install -r labs/rag/requirements.txt` |
| BC-1 Expected outputs are correct | PENDING | Compare output against lab README expected output |
| BC-2 System behaves as described | PENDING | Verify retrieval scores, dedup, token budget |
| BC-5 Outputs deterministic enough | PENDING | Run with `TEMPERATURE=0.0` and compare |

---

## Flags for Human Review

### lab-integration missing (required)

**DOCS_LABS_MAP.md** declares `architecture.md → lab-integration` as `required` with type `module-integration`. This lab does not exist in `labs/rag/`. Neither the module docs README nor the labs README mention it — both describe only 5 labs.

**Decision required:**
- Option A: Create `labs/rag/lab-integration/` implementing the full end-to-end RAG pipeline (chunking → indexing → retrieval → assembly → generation in one script). Update docs README §7 and validation §4.
- Option B: Accept that `lab-query-pipeline` already covers this scope and update DOCS_LABS_MAP to reflect `lab-query-pipeline` as the module-integration lab. Add a note explaining the decision.

This requires a human decision before the module can be declared fully aligned.

---

## Overall Status

**STATIC_PASS / EXECUTION_PENDING**

All static checks pass after fixes. Content quality across all 10 docs is high — comprehensive Why/How/Code structure, strong engineering implications, real failure modes, no placeholders. The module is well-architected and follows the intermediate level policy correctly (ChromaDB + Ollama are justified by the RAG learning objective).

Execution checks and the `lab-integration` alignment question require human action before `FULL_PASS` can be declared.
