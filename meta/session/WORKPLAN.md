# WORKPLAN.md

Phase planner for modules pending authoring (Phase 3 — Advanced, modules 10–16).
Tracks work phases, not individual files. Canonical completion status is in `PROJECT_STATUS.md`.

**Legend:** ⬜ not started · 🔄 in progress · ✅ complete

---

## How to use this file

Each module progresses through five phases in order:

| Phase | What happens |
|-------|-------------|
| 1. Design | Review DOCS_LABS_MAP, LEVEL_MODE; define lab scope; write labs/README |
| 2. Docs | Write in order: README → topics → architecture → implementation-reference → validation |
| 3. Labs | Write labs in sequence per labs/README |
| 4. Static audit | Run `/audit-module` Phase 1; fix SC/IQ failures; update `status: review` |
| 5. Cohesion audit | Run `/audit-module` Phase 2; fix CQ/PQ/EQ/LC failures; update `status: final` |

Execution checks (live infrastructure) are tracked separately in the audit report.
Modules 1–9 are complete — see `PROJECT_STATUS.md` for their audit status.

---

## Phase 3 — Advanced modules

### 10. evaluation-testing

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | |
| 2. Docs | ⬜ | 5 topics + architecture + impl-ref + validation |
| 3. Labs | ⬜ | lab-evaluation-metrics, lab-application-testing, lab-mocking, lab-contract-testing (optional) |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

### 11. safety-guardrails

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | |
| 2. Docs | ⬜ | 5 topics + architecture + impl-ref + validation |
| 3. Labs | ⬜ | lab-input-guardrails, lab-output-guardrails, lab-red-teaming |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

### 12. performance-optimization

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | |
| 2. Docs | ⬜ | 5 topics + architecture + impl-ref + validation |
| 3. Labs | ⬜ | lab-latency-benchmarks, lab-caching, lab-prompt-optimization, lab-batching (optional) |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

### 13. deployment-scaling

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | |
| 2. Docs | ⬜ | 5 topics + architecture + impl-ref + validation |
| 3. Labs | ⬜ | lab-containerization, lab-api-gateway, lab-scaling (optional), lab-iac (optional) |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

### 14. observability-mlops

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | |
| 2. Docs | ⬜ | 5 topics + architecture + impl-ref + validation |
| 3. Labs | ⬜ | lab-tracing, lab-prompt-versioning, lab-continuous-eval |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

### 15. reference-architectures

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | Concept-only module — no labs |
| 2. Docs | ⬜ | pattern-map + 4 reference-architecture docs + validation |
| 3. Labs | — | Not applicable |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

### 16. real-world-projects

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Design | ⬜ | Full projects — define scope per lab |
| 2. Docs | ⬜ | README + validation only |
| 3. Labs | ⬜ | rag-assistant, agent-workflow, java-rag-assistant |
| 4. Static audit | ⬜ | |
| 5. Cohesion audit | ⬜ | |

---

## Last updated

Date: 2026-04-19
