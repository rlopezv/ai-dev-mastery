# VALIDATION TEMPLATE

## Purpose

This document defines the **validation criteria for a step**.

It applies to:

```text id="r2l8n1"
docs/<step>/validation.md
```

Its purpose is to:

- define when a step is considered “complete”
- evaluate understanding
- validate implementation capability
- ensure alignment between docs and labs

This document is **evaluative**, not explanatory.

---

## Frontmatter (MANDATORY)

```yaml id="h9v2k4"
---
id: "<step>-validation"
title: "<Step Name> — Validation"
type: "validation"
step: "<NN-step-name>"
path: "docs/<NN-step-name>/validation.md"
status: "draft"
level: "intermediate"

concepts:
  - "<core-concept-1>"
  - "<core-concept-2>"

prerequisites:
  - "docs/<step>/implementation-reference.md"

next:
  - "<next step>/README.md"

related:
  - "docs/<step>/README.md"

implementation_refs:
  - "labs/<step>/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines criteria to validate understanding and implementation for this step."
---
```

---

## 1. Validation Overview

### Goal

Explain what is being validated.

### Must include

- what the learner should be able to do
- what level of mastery is expected

---

## 2. Conceptual Validation

### Goal

Validate understanding of concepts.

### Format

| Concept   | Validation Method                 |
| --------- | --------------------------------- |
| <concept> | explanation / reasoning / example |

### Rules

- Must cover core concepts of the step
- Must require explanation, not memorization

---

## 3. Practical Validation

### Goal

Validate implementation ability.

### Must include

- tasks or exercises
- expected behavior

### Example

```text id="t1n3q5"
Task: Build a simple retrieval pipeline
Expected: Uses embeddings + vector search + context injection
```

---

## 4. Lab Validation

### Goal

Validate execution of labs.

### Must include

- which labs must run
- what outputs are expected

### Format

| Lab    | Validation Criteria |
| ------ | ------------------- |
| lab-01 | expected output     |
| lab-02 | expected behavior   |

---

## 5. Integration Validation

### Goal

Validate system-level understanding.

### Must include

- how concepts connect
- ability to reason across components

### Example

```text id="b8c4p1"
Explain how retrieval quality affects final LLM output.
```

---

## 6. Failure Detection

### Goal

Identify incorrect understanding.

### Must include

- common misconceptions
- incorrect implementations

### Example

```text id="n7p3v2"
Incorrect: Using raw text instead of embeddings for retrieval
```

---

## 7. Completion Criteria (MANDATORY)

### Goal

Define when the step is complete.

### Must include

- conceptual criteria
- practical criteria
- lab criteria

### Format

```text id="p6m9w4"
A step is complete when:
- All core concepts can be explained
- Required labs execute correctly
- Implementation tasks are completed
- Integration reasoning is correct
```

---

## 8. Self-Assessment Checklist

### Goal

Allow learners to validate themselves.

### Format

```text id="j2k4h7"
- [ ] I understand <concept>
- [ ] I can implement <pattern>
- [ ] I can run <lab>
```

---

## 9. Next Steps

### Goal

Guide progression.

### Must include

- what to revisit if validation fails
- what to do next if validation passes

---

# Structural Rules

This document MUST:

- define validation criteria
- include conceptual and practical validation
- include lab validation
- include completion criteria

This document MUST NOT:

- teach new concepts
- duplicate topic content
- include deep explanations

---

# Writing Rules

This document SHOULD:

- be precise and unambiguous
- use actionable validation criteria
- avoid vague language

This document MUST NOT:

- include theoretical explanations
- rely on implicit understanding

---

# Validation Expectations

Validated using:

```text id="c3l7v9"
meta/standards/validation/docs-checklist.md
```

Critical checks:

- SC-3 (structure present)
- CQ-3 (coverage completeness)
- EQ-1 (engineering relevance)
- IQ-1 (alignment with labs)

---

# Review Expectations

Reviewed using:

```text id="d5q8m2"
meta/standards/review/review-protocol.md
```

Focus:

- completeness of validation criteria
- clarity of requirements
- alignment with docs and labs

---

# Final Rule

A validation document is valid only if:

- it defines measurable criteria
- it covers concepts, implementation, and labs
- it enables self-assessment
- it clearly defines completion

Otherwise:

```text id="v1r6x8"
VALIDATION = NOT ACCEPTABLE
```
