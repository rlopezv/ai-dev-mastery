# meta/standards/validation/labs-checklist.md

## 1. Purpose

This document defines the **validation rules for labs** under:

```text
labs/
```

Its goal is to ensure that labs are:

* executable
* correct
* aligned with documentation
* representative of real system behavior

This checklist is complementary to:

```text
meta/standards/validation/docs-checklist.md
```

---

## 2. Validation Model

Lab validation is based on five categories:

1. Structural Integrity
2. Execution Validity
3. Behavioral Correctness
4. Documentation Alignment
5. Engineering Quality

---

## 3. Scoring System

### 3.1 Scale

Each check is scored:

* **0** → failed
* **1** → partially satisfied
* **2** → satisfied

---

### 3.2 Category Weights

| Category                | Weight |
| ----------------------- | ------ |
| Structural Integrity    | 0.20   |
| Execution Validity      | 0.25   |
| Behavioral Correctness  | 0.25   |
| Documentation Alignment | 0.15   |
| Engineering Quality     | 0.15   |

---

### 3.3 Final Score

```text
FINAL SCORE = weighted sum (0–10)
```

---

### 3.4 Acceptance Criteria

| Result | Condition                            |
| ------ | ------------------------------------ |
| PASS   | Score ≥ 8.0 AND no critical failures |
| FAIL   | Score < 8.0 OR any critical failure  |

---

## 4. Severity Model

* **Critical** → blocks execution or correctness
* **Major** → degrades usefulness
* **Minor** → improvement

---

## 5. Category 1 — Structural Integrity

### LS-1 Lab directory structure is correct

* **Severity:** Critical
* Each lab follows expected folder structure

### LS-2 Lab is isolated

* **Severity:** Major
* No unintended coupling with other labs

### LS-3 Shared utilities are properly scoped

* **Severity:** Major
* Shared code lives only in `shared/`

### LS-4 Required files exist

* **Severity:** Critical
* Entry point, config, or script is present

### LS-5 Naming conventions are respected

* **Severity:** Minor

### LS-6 corpus/ convention is followed (when applicable)

* **Severity:** Major
* Only applies when the module uses a `corpus/` directory
* `corpus/` lives at `labs/<module>/corpus/` — not inside individual lab folders
* `labs/<module>/README.md` includes a "Read the corpus before running the labs" section
* Each corpus file covers one concept, has no frontmatter, and is written in English
* `shared/config.py` exposes a `load_corpus()` function following the standard signature

---

## 6. Category 2 — Execution Validity

### EV-1 Lab runs successfully

* **Severity:** Critical
* No runtime errors

### EV-2 Environment setup is reproducible

* **Severity:** Critical
* Can be executed via documented steps (e.g. docker-compose)

### EV-3 Dependencies are resolved

* **Severity:** Critical

### EV-4 Entry points are functional

* **Severity:** Major
* API / CLI behaves as expected

### EV-5 No manual hidden steps required

* **Severity:** Major

---

## 7. Category 3 — Behavioral Correctness

### BC-1 Expected outputs are correct

* **Severity:** Critical

### BC-2 System behaves as described

* **Severity:** Critical

### BC-3 Edge cases are handled or documented

* **Severity:** Major

### BC-4 Failure modes are visible

* **Severity:** Major

### BC-5 Outputs are deterministic enough for validation

* **Severity:** Major
* (LLM variability allowed but bounded/observable)

---

## 8. Category 4 — Documentation Alignment

### DA-1 Lab maps to documentation topics

* **Severity:** Critical

### DA-2 Implementation reflects concepts

* **Severity:** Critical

### DA-3 Naming matches documentation

* **Severity:** Major

### DA-4 Lab README is accurate and complete

* **Severity:** Major
* Individual lab README (`labs/<module>/lab-<name>/README.md`) must include all mandatory sections from `lab-individual-readme-template.md` in order:
  1. Frontmatter
  2. Overview
  3. Concepts (table)
  4. Setup
  5. Run
  6. Expected Output
  7. What to observe
  8. Concepts verified
  9. Failure case
  10. Infrastructure
* `## What to observe` must contain behavioral guidance specific to the lab's concept — not generic instructions
* `## Failure case` must name the exact modification and list observable symptoms
* The modification described in `## Failure case` must match the `# FAILURE CASE` block in `main.py`
* `## Expected Output` must use real output, not invented values

### DA-5 Cross-references are valid

* **Severity:** Minor

---

## 9. Category 5 — Engineering Quality

### EQ-1 Real system behavior is represented

* **Severity:** Major

### EQ-2 Trade-offs are visible

* **Severity:** Minor

### EQ-3 Performance constraints are acknowledged

* **Severity:** Minor

### EQ-4 Observability exists

* **Severity:** Major
* logs / outputs / traceability

### EQ-5 No misleading simplifications

* **Severity:** Major

---

## 10. Validation Output Format

```text
LAB_VALIDATION_RESULT
TARGET:

FINAL SCORE:
STATUS: PASS | FAIL

CRITICAL FAILURES:
- ...

MAJOR ISSUES:
- ...

MINOR ISSUES:
- ...

REQUIRED FIXES:
- ...
```

---

## 11. Interpretation Rules

### PASS

* Lab is executable and correct
* Minor issues may exist

### FAIL

* Lab cannot run OR produces incorrect results
* Must be fixed before use

---

## 12. Non-Compliant Validation Behavior

Invalid validation includes:

* "works on my machine"
* no execution performed
* skipping runtime validation
* ignoring behavioral mismatches
* validating only structure without execution

---

## 13. Final Rule

A lab is considered valid only if:

* it executes successfully
* it produces correct behavior
* it aligns with documentation
* it passes scoring criteria

Otherwise:

```text
LAB = NOT ACCEPTABLE
```
