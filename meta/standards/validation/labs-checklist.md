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

Lab validation is based on six categories:

1. Structural Integrity
2. Execution Validity
3. Behavioral Correctness
4. Documentation Alignment
5. Engineering Quality
6. Level Compliance

---

## 3. Scoring System

### 3.1 Scale

Each check is scored:

* **0** → failed
* **1** → partially satisfied
* **2** → satisfied

---

### 3.2 Category Weights

| Category | Checks | Max Raw | Weight | Max Weighted |
|----------|--------|---------|--------|--------------|
| Structural Integrity    | 8 (LS-1..LS-8) | 16 | 0.15 | 1.5 |
| Execution Validity      | 5 (EV-1..EV-5) | 10 | 0.25 | 2.5 |
| Behavioral Correctness  | 5 (BC-1..BC-5) | 10 | 0.25 | 2.5 |
| Documentation Alignment | 5 (DA-1..DA-5) | 10 | 0.10 | 1.0 |
| Engineering Quality     | 5 (EQ-1..EQ-5) | 10 | 0.10 | 1.0 |
| Level Compliance        | 5 (LC-1..LC-5) | 10 | 0.15 | 1.5 |

---

### 3.3 Final Score

```text
CATEGORY SCORE = (raw score / max raw score) × max weighted score
FINAL SCORE = sum of all category scores (0–10)
```

Examples:

```text
Structural Integrity raw = 12/16
Weighted = (12/16) × 1.5 = 1.125

Execution Validity raw = 9/10
Weighted = (9/10) × 2.5 = 2.25
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
* Each lab follows expected folder structure, including the mandatory `## Navigation` breadcrumb in README files with a correct path to the parent labs README

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

### LS-7 Frontmatter is present and valid

* **Severity:** Critical
* Every `labs/<module>/README.md` and `labs/<module>/lab-<name>/README.md` includes frontmatter compliant with `meta/standards/templates/lab-entry-readme-scaffold.md` and `meta/standards/templates/lab-individual-readme-scaffold.md` respectively
* `corpus/` files and utility READMEs (e.g. `shared/`) are exempt

### LS-8 H1 heading is present after frontmatter

* **Severity:** Critical
* The first non-empty line after the closing `---` of frontmatter is `# <Title>`, matching the `title` field in frontmatter

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

### DA-3 Naming matches documentation and glossary

* **Severity:** Major
* Every term in the `concepts` frontmatter field must be present in `docs/reference/glossary.md`.
  * If a term is **absent**: add it to the glossary before accepting the lab (per CLAUDE.md §7).
  * If a term is **present with a different name**: update the lab to use the canonical glossary term — no paraphrases, renamed variants, or abbreviations.

### DA-4 Lab README is accurate and complete

* **Severity:** Major
* Individual lab README (`labs/<module>/lab-<name>/README.md`) must include all mandatory sections from `lab-individual-readme-scaffold.md` in order:
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

## 10. Category 6 — Level Compliance

Full contract: `meta/system-design/LEVEL_MODE.md`

### LC-1 Infrastructure profile matches declared level

* **Severity:** Critical
* The lab uses the profile(s) permitted by the module's declared level (foundational / intermediate / advanced)

### LC-2 Runtime components are justified by the learning objective

* **Severity:** Major
* Every service or dependency required by the lab is directly justified by what the lab teaches

### LC-3 Abstraction level matches level policy

* **Severity:** Major
* Lab code follows the abstraction policy for its level: raw APIs for foundational, transparent frameworks for intermediate, explicit trade-offs for advanced

### LC-4 Observability is sufficient for the declared level

* **Severity:** Major
* Outputs and logs allow the learner to understand behavior at the expected depth for the declared level

### LC-5 Level exceptions are explicitly documented

* **Severity:** Critical
* If the lab deviates from the default profile of its level, the exception is documented in the lab README, the module labs README, and the infrastructure README (G-5)

---

## 11. Scoring Sheet

Use the following structure when validating a lab.

| Check | Score (0/1/2) | Severity | Notes |
|-------|----------------|----------|-------|
| LS-1 |  | Critical |  |
| LS-2 |  | Major |  |
| LS-3 |  | Major |  |
| LS-4 |  | Critical |  |
| LS-5 |  | Minor |  |
| LS-6 |  | Major |  |
| LS-7 |  | Critical |  |
| LS-8 |  | Critical |  |
| EV-1 |  | Critical |  |
| EV-2 |  | Critical |  |
| EV-3 |  | Critical |  |
| EV-4 |  | Major |  |
| EV-5 |  | Major |  |
| BC-1 |  | Critical |  |
| BC-2 |  | Critical |  |
| BC-3 |  | Major |  |
| BC-4 |  | Major |  |
| BC-5 |  | Major |  |
| DA-1 |  | Critical |  |
| DA-2 |  | Critical |  |
| DA-3 |  | Major |  |
| DA-4 |  | Major |  |
| DA-5 |  | Minor |  |
| EQ-1 |  | Major |  |
| EQ-2 |  | Minor |  |
| EQ-3 |  | Minor |  |
| EQ-4 |  | Major |  |
| EQ-5 |  | Major |  |
| LC-1 |  | Critical |  |
| LC-2 |  | Major |  |
| LC-3 |  | Major |  |
| LC-4 |  | Major |  |
| LC-5 |  | Critical |  |

---

## 12. Validation Output Format

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

## 13. Interpretation Rules

### PASS

* Lab is executable and correct
* Minor issues may exist

### FAIL

* Lab cannot run OR produces incorrect results
* Must be fixed before use

---

## 14. Non-Compliant Validation Behavior

Invalid validation includes:

* "works on my machine"
* no execution performed
* skipping runtime validation
* ignoring behavioral mismatches
* validating only structure without execution

---

## 15. Final Rule

A lab is considered valid only if:

* it executes successfully
* it produces correct behavior
* it aligns with documentation
* it passes scoring criteria

Otherwise:

```text
LAB = NOT ACCEPTABLE
```
