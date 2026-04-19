# audit-report-format.md

## Purpose

Defines the canonical format for audit reports in `meta/audit/reports/` and the check result
states used across all audit output. All reports must conform to this structure.

---

## Report Types

| File | Produced by | Lifecycle |
|------|------------|-----------|
| `<module>.audit.md` | `/audit-module` | Created on first audit; Phase 2 section appended when cohesion audit completes — Phase 1 is never rewritten |
| `global.audit.md` | `/audit` | Replaced on each run |
| `enrich.md` | `/enrich` | Replaced on each run |

Individual document audits (`/audit-doc`) update the relevant rows inside the module's
`<module>.audit.md` rather than producing separate files.

---

## Check Result States

| State | Meaning |
|-------|---------|
| `PASS` | Check formally applied and passed |
| `FAIL` | Check formally applied and failed |
| `FIXED` | Check failed but corrected during the audit — written as `FAIL → FIXED` |
| `PENDING` | Check deferred — will be applied in a future phase or when infrastructure is available |
| `SKIP` | Check not applicable to this document or module type |

`FIXED` is not a standalone state — it qualifies a `FAIL`.

**PENDING vs SKIP:** Use `PENDING` when the check _will_ be applied: Phase 2 checks in a Phase 1 report, and execution checks awaiting live infrastructure. Use `SKIP` only when the check is genuinely not applicable (e.g., lab structure checks for a module with no labs).

---

## Module Audit Report (`<module>.audit.md`)

### Header

```markdown
# Audit Report: <module>

**Date:** YYYY-MM-DD
**Branch:** <branch>
**Auditor:** Claude Code
```

---

### Scope

```markdown
## Scope

| Category | Files |
|----------|-------|
| Docs     | `docs/<module>/README.md`, `<topic>.md`, ... |
| Labs     | `labs/<module>/README.md`, `lab-<n>/`, ... |
| Shared   | `labs/<module>/shared/` (if applicable) |
| Alignment | `meta/system-design/DOCS_LABS_MAP.md` §<module> |
| Glossary  | `docs/reference/glossary.md` |
```

---

### Phase 1 — Static

Covers structural and alignment checks verifiable without executing the labs or reading
content for correctness.

```markdown
## Phase 1 — Static

### Structural Compliance

| Check | Result | Notes |
|-------|--------|-------|
| SC-1 Frontmatter valid             | PASS/FAIL/SKIP | |
| SC-2 Document type matches artifact | PASS/FAIL/SKIP | |
| SC-3 Navigation breadcrumb present  | PASS/FAIL/SKIP | |
| SC-4 No placeholders               | PASS/FAIL/SKIP | |
| SC-5 Tables present where required  | PASS/FAIL/SKIP | |
| SC-6 H1 matches frontmatter title   | PASS/FAIL/SKIP | |

### Integration Quality (static)

| Check | Result | Notes |
|-------|--------|-------|
| IQ-5 Fits roadmap position                  | PASS/FAIL/SKIP | |
| IQ-6 Concepts in glossary (canonical names) | PASS/FAIL/FIXED | |

### Lab Structure

| Check | Result | Notes |
|-------|--------|-------|
| All required sections present    | PASS/FAIL/SKIP | |
| Lab optional/required alignment  | PASS/FAIL/SKIP | |

### DOCS_LABS_MAP Alignment

| Doc | Lab | Type | Required | Present |
|-----|-----|------|----------|---------|

### Glossary Check (IQ-6)

| Concept (frontmatter) | Glossary entry | Status |
|-----------------------|----------------|--------|

### Cross-Reference Validation

| Reference | Exists |
|-----------|--------|
```

---

### Phase 2 — Cohesion

Added when the formal cohesion audit completes. Until then this section is absent and
cohesion checks appear as `PENDING` at the bottom of Phase 1 under "Checks Not Applied".

```markdown
## Phase 2 — Cohesion

### Content Quality

| Check | Result | Notes |
|-------|--------|-------|
| CQ-1 Concepts technically correct   | PASS/FAIL/SKIP | |
| CQ-2 Explanations causal            | PASS/FAIL/SKIP | |
| CQ-3 Coverage complete              | PASS/FAIL/SKIP | |
| CQ-4 Terminology consistent         | PASS/FAIL/SKIP | |
| CQ-5 Limitations acknowledged       | PASS/FAIL/SKIP | |

### Pedagogical Quality

| Check | Result | Notes |
|-------|--------|-------|
| PQ-1 Explanation progressive        | PASS/FAIL/SKIP | |
| PQ-2 Reader assumptions appropriate | PASS/FAIL/SKIP | |
| PQ-3 Mental models clear            | PASS/FAIL/SKIP | |
| PQ-4 Examples meaningful            | PASS/FAIL/SKIP | |
| PQ-5 Tables reduce cognitive load   | PASS/FAIL/SKIP | |

### Engineering Quality

| Check | Result | Notes |
|-------|--------|-------|
| EQ-1 Engineering implications explicit  | PASS/FAIL/SKIP | |
| EQ-2 Trade-offs identified              | PASS/FAIL/SKIP | |
| EQ-3 Real system behavior reflected     | PASS/FAIL/SKIP | |
| EQ-4 Abstract explanation grounded      | PASS/FAIL/SKIP | |
| EQ-5 Operational risks mentioned        | PASS/FAIL/SKIP | |

### Integration Quality (cohesion)

| Check | Result | Notes |
|-------|--------|-------|
| IQ-1 Sandbox alignment                  | PASS/FAIL/SKIP | |
| IQ-2 Cross-references meaningful        | PASS/FAIL/SKIP | |
| IQ-3 Implementation references concrete | PASS/FAIL/SKIP | |
| IQ-4 Validation references present      | PASS/FAIL/SKIP | |

### Level Compliance

| Check | Result | Notes |
|-------|--------|-------|
| LC-1 Runtime complexity matches level       | PASS/FAIL/SKIP | |
| LC-2 Components justified                   | PASS/FAIL/SKIP | |
| LC-3 Abstraction level appropriate          | PASS/FAIL/SKIP | |
| LC-4 Observability requirements addressed   | PASS/FAIL/SKIP | |
| LC-5 Level exceptions documented            | PASS/FAIL/SKIP | |
```

---

### Fixes Applied During Audit

```markdown
## Fixes Applied During Audit

1. **Term** — description of what was wrong and what was changed.

None. (if no fixes were needed)
```

---

### Phase 3 — Execution

Present after Phase 1 as a placeholder with all checks PENDING. Filled in when live
infrastructure is available (Ollama running, devcontainer active).

Phase 3 checks map to `meta/standards/validation/labs-checklist.md` categories:

| labs-checklist category | Check IDs applied in Phase 3 |
|-------------------------|-------------------------------|
| Execution Validity | EV-1, EV-2, EV-3, EV-4, EV-5 |
| Behavioral Correctness | BC-1, BC-2, BC-3, BC-4, BC-5 |

Structural Integrity (LS-*), Documentation Alignment (DA-*), Engineering Quality (EQ-*),
and Level Compliance (LC-*) are applied in Phase 1 (static) for labs.

```markdown
## Phase 3 — Execution

| Check | Status | What to verify |
|-------|--------|----------------|
| EV-1 Labs run without error | PENDING | Requires live infrastructure — `python lab-<n>/main.py` exits 0 |
| EV-2 Environment reproducible | PENDING | Requires live infrastructure |
| EV-3 Dependencies resolved | PENDING | Requires live infrastructure |
| EV-4 Entry points functional | PENDING | Requires live infrastructure |
| EV-5 No hidden manual steps | PENDING | Requires live infrastructure |
| BC-1 Expected outputs correct | PENDING | Requires live infrastructure |
| BC-2 System behaves as described | PENDING | Requires live infrastructure |
| BC-3 Edge cases handled | PENDING | Requires live infrastructure |
| BC-4 Failure modes visible | PENDING | Requires live infrastructure |
| BC-5 Outputs deterministic enough | PENDING | Requires live infrastructure |
```

---

### Overall Status

```markdown
## Overall Status

**STATIC_PASS | COHESION_PENDING | EXECUTION_PENDING**

- Summary bullet points.
```

Valid status combinations:

| Status string | Meaning |
|---------------|---------|
| `STATIC_PASS \| COHESION_PENDING \| EXECUTION_PENDING` | Phase 1 complete, phases 2 and 3 not started |
| `STATIC_PASS \| COHESION_PASS \| EXECUTION_PENDING` | Phases 1 and 2 complete, labs not run |
| `STATIC_PASS \| COHESION_PENDING \| EXECUTION_SKIP` | Phase 1 complete, module has no labs |
| `STATIC_PASS \| COHESION_PASS \| EXECUTION_SKIP` | Phases 1 and 2 complete, module has no labs |
| `FULL_PASS` | All three phases complete and passing |

---

## Relationship to Other Standards

| Standard | Role |
|----------|------|
| `meta/standards/validation/docs-checklist.md` | Defines all checks (SC, CQ, PQ, EQ, IQ, LC) applied in Phase 1 and Phase 2 |
| `meta/standards/validation/labs-checklist.md` | Defines lab checks (LS, DA) applied in Phase 1 |
| `meta/standards/review/review-protocol.md` | Human-facing diagnostic instrument — used by `/review-doc`, not by audit commands |

---

## Report Storage Policy

| Directory | Contents | Committed | Lifecycle |
|-----------|----------|-----------|-----------|
| `meta/audit/reports/` | `<module>.audit.md`, `global.audit.md`, `enrich.md` | Yes | Persistent — never deleted, only appended or replaced |
| `meta/session/reports/` | `<filename>.review.md` from `/review-doc` | No | Within-session — consumed and deleted by `/fix-doc` |
