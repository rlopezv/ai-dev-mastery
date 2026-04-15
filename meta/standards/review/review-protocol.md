# review-protocol.md

## Purpose

This document defines the review protocol for learner-facing documentation under `docs/`.
Review is diagnostic, not generative.

The reviewer must identify, classify, and explain issues.
The reviewer must not rewrite the document or introduce new content directly.

---

## 1. Review Categories

All reviews must cover these five categories.

### 1.1 Conceptual

- Missing or incorrect concepts
- Shallow explanations
- Broken conceptual chains

### 1.2 Pedagogical

- Confusing sections or excessive cognitive jumps
- Poor sequencing
- Missing intuition before mechanics

### 1.3 Engineering

- Missing trade-offs
- Lack of real-world implications
- Ungrounded abstractions

### 1.4 Structural

- Missing or misplaced sections
- Poor table usage
- Template non-compliance

### 1.5 Consistency

- Terminology inconsistencies within the document
- Misalignment with other modules or the architecture
- Conflicts with `docs/reference/glossary.md`

---

## 2. Issue Severity

| Severity | Meaning |
|----------|---------|
| Critical | Blocks understanding or correctness |
| Major | Significantly degrades quality |
| Minor | Improvement opportunity, does not block |

---

## 3. Issue Format

```text
ISSUE-NN
CATEGORY:     Conceptual | Pedagogical | Engineering | Structural | Consistency
SEVERITY:     Critical | Major | Minor
LOCATION:     <section name or line reference>
DESCRIPTION:  <what is wrong>
IMPACT:       <effect on the reader>
FIX:          <concrete suggested fix>
```

---

## 4. Review Output

```text
REVIEW_RESULT
TARGET: <file path>

SUMMARY:
<2-3 sentence overall assessment>

CRITICAL ISSUES:
- ISSUE-01 ...

MAJOR ISSUES:
- ISSUE-02 ...

MINOR ISSUES:
- ISSUE-03 ...

RECOMMENDED ACTION: ACCEPT | REVISE | REJECT
```

**ACCEPT** — no critical issues, score ≥ 8. Minor issues may remain.
**REVISE** — major issues present, document is recoverable.
**REJECT** — critical issues that require structural rework.

---

## 5. Reviewer Rules

Must:
- Cover all five categories
- Be explicit and concrete — no generic statements
- Justify every severity assignment
- Propose actionable fixes

Must not:
- Skip categories
- Rewrite the document
- Provide vague feedback ("needs improvement")
- Override validation scoring rules

---

## 6. Review ↔ Validation Relationship

Review and validation are distinct but connected. Review identifies problems.
Validation scores compliance (`meta/standards/validation/docs-checklist.md`).

Every Critical issue must correspond to at least one failed Critical check
in the validation checklist.
