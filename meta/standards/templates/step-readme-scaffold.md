# step-readme-scaffold.md

## Frontmatter (MANDATORY)

```yaml
---
id: "<step>-readme"
title: "<Step Name>"
type: "step-readme"
step: "<NN-step-name>"
path: "docs/<NN-step-name>/README.md"
status: "draft"
level: "foundational | intermediate | advanced"

concepts:
  - "<core-concept-1>"
  - "<core-concept-2>"

prerequisites:
  - "<previous step or doc>"

next:
  - "<first topic of this step>"

related:
  - "<related step or topic>"

implementation_refs:
  - "labs/<step>/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Introduces the scope and structure of this step."
---
```

---

## 1. Overview

What this step is about, why it matters, and what capability it unlocks.

---

## 2. Scope

What is covered and what is NOT covered.

---

## 3. Key Concepts

The core ideas introduced in this step.

---

## 4. Concept Map

Relationships between concepts. Diagram preferred; structured list as fallback.

---

## 5. Learning Flow

Order of topics and dependencies between them.

---

## 6. Documentation Structure

```text
docs/<step>/
├── README.md
├── <topic-1>.md
├── <topic-2>.md
├── architecture.md
├── implementation-reference.md
└── validation.md
```

---

## 7. Labs Overview

| Lab | Purpose |
|-----|---------|
| lab-01 | observation |
| lab-02 | implementation |

---

## 8. How to Use This Step

Recommended path and any optional paths.

---

## 9. Relationship to Other Steps

What comes before and what comes after in the roadmap.

---

## 10. Next Steps

Direct link to the first topic or next step.
