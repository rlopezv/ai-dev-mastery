# PROJECT_STATUS.md

## Purpose

This file tracks the progress of the AI Dev Mastery tutorial.
It is updated by Claude Code at the end of every completed task.
Do not edit manually unless correcting an error.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Complete — validated and committed |
| 🔄 | In progress |
| ⬜ | Not started |
| — | Not applicable |

---

## Meta

| File | Status |
|------|--------|
| `CLAUDE.md` | ✅ |
| `meta/system-design/REPOSITORY_LAYOUT.md` | ✅ |
| `meta/system-design/DOCS_LABS_MAP.md` | ✅ |
| `meta/standards/writing/writing-style.md` | ✅ |
| `meta/standards/writing/lab-code-style.md` | ✅ |
| `meta/standards/templates/topic-template.md` | ✅ |
| `meta/standards/templates/implementation-reference-template.md` | ✅ |
| `meta/standards/templates/reference-architecture-template.md` | ✅ |
| `meta/standards/validation/docs-checklist.md` | ✅ |
| `meta/standards/validation/labs-checklist.md` | ✅ |
| `meta/standards/review/review-protocol.md` | ✅ |
| `meta/workflow/CLAUDE-CODE-WORKFLOW.md` | ✅ |
| `docs/reference/glossary.md` | 🔄 |
| `meta/` review pass | ✅ |

---

## Modules

| Module | README | Topics | Architecture | Impl. Ref. | Validation | Labs |
|--------|--------|--------|--------------|------------|------------|------|
| `llm-fundamentals` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `llm-apis` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `prompt-engineering` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `structured-outputs` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `rag` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `memory-context` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ai-agents` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `frameworks-tools` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `ai-java` | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| `evaluation-testing` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `safety-guardrails` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `performance-optimization` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `deployment-scaling` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `observability-mlops` | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| `reference-architectures` | ⬜ | ⬜ | — | ⬜ | ⬜ | ⬜ |
| `real-world-projects` | ⬜ | — | — | — | ⬜ | ⬜ |

---

## Audit status

| Module | Audit | Report |
|--------|-------|--------|
| `llm-fundamentals` | STATIC_PASS \| COHESION_PASS \| EXECUTION_PENDING | `meta/audit/reports/llm-fundamentals.audit.md` |
| `llm-apis` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/llm-apis.audit.md` |
| `prompt-engineering` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/prompt-engineering.audit.md` |
| `structured-outputs` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/structured-outputs.audit.md` |
| `rag` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/rag.audit.md` |
| `memory-context` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/memory-context.audit.md` |
| `ai-agents` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/ai-agents.audit.md` |
| `frameworks-tools` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING | `meta/audit/reports/frameworks-tools.audit.md` |
| `ai-java` | STATIC_PASS \| COHESION_PENDING \| EXECUTION_SKIP | `meta/audit/reports/ai-java.audit.md` |

---

## Last updated

Session: Cohesion audit (Phase 2) complete for llm-fundamentals — COHESION_PASS. All 10 docs pass all checks; status updated to `final`. Script bug fixed: sync-frontmatter-status.py now handles quoted YAML status values. 8 modules remain in COHESION_PENDING.
Date: 2026-04-19
