# meta/standards/validation/docs-checklist.md

## 1. Purpose

This document defines the **canonical validation checklist** for learner-facing documentation under:

```text
docs/
```

Its purpose is to convert quality expectations into an **explicit, repeatable, and scorable validation system**.

It is used by:

- review workflows
- integration workflows
- session closure
- acceptance decisions

This checklist validates documentation quality.  
It does NOT validate repository structure or bootstrap completeness.

---

## 2. Validation Model

Validation is performed across five categories:

1. Structural Compliance
2. Content Quality
3. Pedagogical Quality
4. Engineering Quality
5. Integration Quality

Each category includes:

- checks
- severity
- score weight
- blocking behavior

---

## 3. Scoring System

### 3.1 Scoring Scale

Each check is scored as:

- **0** → failed
- **1** → partially satisfied
- **2** → satisfied

### 3.2 Weighted Categories

| Category | Max Raw Score | Weight | Max Weighted Score |
|---------|----------------|--------|--------------------|
| Structural Compliance | 10 | 0.25 | 2.5 |
| Content Quality | 10 | 0.20 | 2.0 |
| Pedagogical Quality | 10 | 0.20 | 2.0 |
| Engineering Quality | 10 | 0.20 | 2.0 |
| Integration Quality | 10 | 0.15 | 1.5 |

### 3.3 Final Score

The final score is calculated on a 0–10 scale.

```text
FINAL SCORE = sum(weighted category scores)
```

### 3.4 Acceptance Threshold

| Result | Condition |
|--------|-----------|
| PASS | Final score ≥ 8.0 AND no critical failures |
| FAIL | Final score < 8.0 OR one or more critical failures |

---

## 4. Severity Model

Each check is classified as one of:

- **Critical** → failure blocks acceptance
- **Major** → failure significantly degrades quality
- **Minor** → failure should be corrected but does not block by itself

### 4.1 Critical Failure Rule

A document automatically fails if any Critical check scores:

```text
0 = failed
```

A Critical check scored as:

```text
1 = partially satisfied
```

does not auto-fail, but it must be explicitly called out for correction before final acceptance if it affects reader comprehension or structural integrity.

---

## 5. Category 1 — Structural Compliance

### SC-1 Frontmatter is present and valid
- **Severity:** Critical
- **Rule:** Document includes frontmatter compliant with `meta/standards/frontmatter/frontmatter-spec.md`

### SC-2 Document type matches intended artifact
- **Severity:** Major
- **Rule:** The document structure matches its declared type (`step-readme`, `topic`, `architecture`, etc.)

### SC-3 Required section structure is present
- **Severity:** Critical
- **Rule:** The document follows the required internal structure for its type and phase expectations

### SC-4 No placeholders or unfinished sections remain
- **Severity:** Critical
- **Rule:** No `TODO`, `TBD`, `...`, “example”, or clearly incomplete sections remain

### SC-5 Tables are present where required
- **Severity:** Major
- **Rule:** Required synthesis/comparison tables exist and are not empty

---

## 6. Category 2 — Content Quality

### CQ-1 Concepts are technically correct
- **Severity:** Critical
- **Rule:** Core concepts are correct and do not contain misleading explanations

### CQ-2 Explanations are causal, not merely descriptive
- **Severity:** Major
- **Rule:** The document explains why/how, not only what

### CQ-3 Coverage is complete for the stated objective
- **Severity:** Major
- **Rule:** The document fulfills its declared purpose without obvious missing core material

### CQ-4 Terminology is consistent
- **Severity:** Major
- **Rule:** The same concept is named consistently throughout the document

### CQ-5 Limitations, failure modes, or boundaries are acknowledged
- **Severity:** Major
- **Rule:** The document identifies constraints, trade-offs, or limits when relevant

---

## 7. Category 3 — Pedagogical Quality

### PQ-1 Explanation is progressive
- **Severity:** Major
- **Rule:** The document moves from intuition to mechanics to implications in a way that reduces cognitive load

### PQ-2 Reader assumptions are appropriate
- **Severity:** Critical
- **Rule:** The text does not assume deep ML knowledge beyond the declared audience

### PQ-3 Mental models are clear
- **Severity:** Major
- **Rule:** The document provides usable conceptual framing, not only terminology

### PQ-4 Examples are meaningful
- **Severity:** Major
- **Rule:** Examples clarify the concept and are not generic filler

### PQ-5 Tables reduce cognitive load
- **Severity:** Minor
- **Rule:** Tables are used for synthesis, comparison, or navigation rather than decoration

---

## 8. Category 4 — Engineering Quality

### EQ-1 Engineering implications are explicit
- **Severity:** Critical
- **Rule:** The document makes practical engineering consequences visible

### EQ-2 Trade-offs are identified
- **Severity:** Major
- **Rule:** Relevant design trade-offs are explained

### EQ-3 Real system behavior is reflected
- **Severity:** Major
- **Rule:** The document connects ideas to actual implementation or runtime behavior

### EQ-4 Abstract explanation is grounded
- **Severity:** Major
- **Rule:** The document is not purely conceptual when engineering grounding is expected

### EQ-5 Operational risks or common errors are mentioned
- **Severity:** Major
- **Rule:** The document identifies likely mistakes, boundary conditions, or operational pitfalls when relevant

---

## 9. Category 5 — Integration Quality

### IQ-1 Sandbox or implementation alignment is present
- **Severity:** Major
- **Rule:** The document aligns with the intended sandbox/runtime model where applicable

### IQ-2 Cross-references are meaningful
- **Severity:** Minor
- **Rule:** References to other steps/docs are useful and not arbitrary

### IQ-3 Implementation references are concrete
- **Severity:** Major
- **Rule:** Links or references to labs/files/endpoints are real, relevant, and specific when expected

### IQ-4 Validation references are present
- **Severity:** Minor
- **Rule:** Validation references exist and are consistent with the standards layer

### IQ-5 Document fits the roadmap position
- **Severity:** Major
- **Rule:** The document is coherent with what comes before and after in the roadmap

---

## 10. Scoring Sheet

Use the following structure when validating a document.

| Check | Score (0/1/2) | Severity | Notes |
|------|----------------|----------|-------|
| SC-1 |  | Critical |  |
| SC-2 |  | Major |  |
| SC-3 |  | Critical |  |
| SC-4 |  | Critical |  |
| SC-5 |  | Major |  |
| CQ-1 |  | Critical |  |
| CQ-2 |  | Major |  |
| CQ-3 |  | Major |  |
| CQ-4 |  | Major |  |
| CQ-5 |  | Major |  |
| PQ-1 |  | Major |  |
| PQ-2 |  | Critical |  |
| PQ-3 |  | Major |  |
| PQ-4 |  | Major |  |
| PQ-5 |  | Minor |  |
| EQ-1 |  | Critical |  |
| EQ-2 |  | Major |  |
| EQ-3 |  | Major |  |
| EQ-4 |  | Major |  |
| EQ-5 |  | Major |  |
| IQ-1 |  | Major |  |
| IQ-2 |  | Minor |  |
| IQ-3 |  | Major |  |
| IQ-4 |  | Minor |  |
| IQ-5 |  | Major |  |

---

## 11. Category Calculation Method

Each category has 5 checks, each with a max raw score of 2.

So each category has:

```text
MAX RAW SCORE = 10
```

To calculate a weighted category score:

```text
CATEGORY SCORE = (raw score / 10) × category weight × 10
```

Example:

```text
Structural Compliance raw = 8/10
Weighted = (8/10) × 2.5 = 2.0
```

Repeat for all categories and sum the results.

---

## 12. Validation Output Format

Every validation result SHOULD produce:

```text
VALIDATION_RESULT
TARGET:
TYPE:
FINAL SCORE:
STATUS: (PASS | FAIL)

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

## 13. Interpretation Guidelines

### PASS does NOT mean perfect
A document may pass while still containing minor improvements.

### FAIL does NOT mean unusable
A document may contain useful content but remain below repository standard.

### Reviewers must be explicit
A reviewer MUST explain why a score was assigned whenever a check is scored 0 or 1.

---

## 14. Non-Compliant Validation Behavior

The following are invalid validation behaviors:

- assigning PASS without scoring
- assigning score without notes
- ignoring critical failures
- validating against personal taste rather than stated rules
- skipping categories because the reviewer considers them “obvious”

---

## 15. Final Rule

A learner-facing document is considered accepted only if:

- it has been scored using this checklist
- final score is **≥ 8.0**
- no critical failures remain
- required fixes, if any, have been applied before final acceptance
