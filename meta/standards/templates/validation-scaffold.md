# validation-scaffold.md

## Frontmatter (MANDATORY)

```yaml
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

## Navigation

[Docs](../../README.md) / [<Module Name>](README.md) / Validation

---

## 1. Validation Overview

What the learner should be able to do and what level of mastery is expected.

---

## 2. Conceptual Validation

| Concept     | Validation Method                 |
| ----------- | --------------------------------- |
| \<concept\> | explanation / reasoning / example |

---

## 3. Practical Validation

Tasks or exercises with expected behavior.

```text
Task: Build a simple retrieval pipeline
Expected: Uses embeddings + vector search + context injection
```

---

## 4. Lab Validation

| Lab    | Validation Criteria |
| ------ | ------------------- |
| lab-01 | expected output     |
| lab-02 | expected behavior   |

---

## 5. Integration Validation

How concepts connect and what system-level reasoning is expected.

---

## 6. Failure Detection

Common misconceptions and incorrect implementations to watch for.

---

## 7. Completion Criteria (MANDATORY)

A step is complete when:

- All core concepts can be explained
- Required labs execute correctly
- Implementation tasks are completed
- Integration reasoning is correct

---

## 8. Self-Assessment Checklist

```text
- [ ] I understand <concept>
- [ ] I can implement <pattern>
- [ ] I can run <lab>
```

---

## 9. Next Steps

What to revisit if validation fails. What to do next if validation passes.
