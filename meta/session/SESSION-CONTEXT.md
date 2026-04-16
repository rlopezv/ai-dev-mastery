# SESSION-CONTEXT.md

Update this file at the end of each working session to capture:
- decisions made
- files modified
- pending items for the next session

---

## Last session

**Date:** 2026-04-16
**Phase:** Fase 4 — rag module complete + repo-wide structural and editorial fixes

---

### Completed — rag module

- All 5 rag labs written and validated: lab-embeddings, lab-chunking-strategies, lab-retrieval-playground, lab-query-pipeline, lab-rag-evaluation
- Bug fixed: `labs/rag/lab-rag-evaluation/main.py` — removed invalid conditional import for `SYSTEM_PROMPT`

---

### Completed — repo-wide fixes

**Language rule formalized:**
- `CLAUDE.md` — new section 5 "Language": all learner-facing output in English regardless of conversation language; covers `docs/`, `labs/`, `infrastructure/`, all `README.md` files
- `meta/standards/writing/writing-style.md` — scope expanded from "docs/ only" to all learner-facing files in the repository

**corpus/ convention documented:**
- `meta/standards/writing/lab-code-style.md` — new section 9: when to use corpus/, `load_corpus()` signature convention, README requirement, content rules
- `labs/rag/README.md` — removed reference to `meta/` (not learner-facing); corpus section now stands on its own

**README files written:**
- `README.md` — rewritten in English: intro, repo structure, Modules table (#/Module/Level/Docs/Labs with ✅/⬜), Getting Started, Labs table (#/Module/Labs/Status), links to docs/README and labs/README
- `docs/README.md` — new: navigation order within a module, document types table, module index with descriptions and status
- `labs/README.md` — new: infrastructure profiles (light/full) mapped to modules, runtime prerequisites, conventions (shared/, corpus/, .env, execution order), module index with lab names and status
- `infrastructure/README.md` — translated to English (services, profiles, hardware config, models, verification commands)

### Key decisions

- Root README is the master index (Modules + Labs tables). `docs/README.md` and `labs/README.md` have their own indexes with different columns — not duplication, different views.
- Labs section in root README follows same table structure as Modules section (was a loose link before).
- `corpus/` is a per-module convention, not a shared global resource. Each module that needs a fixed document set gets its own `corpus/` under `labs/<module>/`.
- `meta/` files are internal — never referenced from learner-facing content.

---

## Pending — next session

### 1. meta/ review pass (BEFORE writing any new module)

Several conventions changed this session. Review `meta/` for consistency before proceeding:
- README conventions reflected in `REPOSITORY_LAYOUT.md` and templates
- corpus/ pattern added to `labs-checklist.md`
- Language rule added to `lab-code-style.md` (currently missing there)
- Status columns in learner-facing tables vs `PROJECT_STATUS.md` as source of truth
- `infrastructure/README.md` reflected in `REPOSITORY_LAYOUT.md`

See memory file `project_meta_review_pending.md` for full checklist.

### 2. Module 6: `memory-context`

> `/write-module memory-context`
> `/design-labs memory-context`
