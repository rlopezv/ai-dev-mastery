# lab-entry-readme-template.md

## Frontmatter (MANDATORY)

```yaml
---
id: "<step>-labs-readme"
title: "<Step Name> — Labs"
type: "lab-readme"
step: "<NN-step-name>"
path: "labs/<NN-step-name>/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "<concept-1>"
  - "<concept-2>"

prerequisites:
  - "<docs reference or step>"

next:
  - "<next step or lab>"

related:
  - "docs/<step>/README.md"

implementation_refs:
  - "labs/<step>/lab-01-<n>"
  - "labs/<step>/lab-02-<n>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how to run and understand the labs for this step."
---
```

---

## 1. Overview

What these labs implement, why they exist in this step, and what is NOT covered.

---

## 2. Lab Inventory

| Lab | Description | Type |
|-----|-------------|------|
| lab-01-\<n\> | \<what it demonstrates\> | observation / implementation |
| lab-02-\<n\> | \<what it builds\> | implementation |

---

## 3. Execution Model

How labs are run: docker-compose usage, services involved, entry points.

```bash
docker-compose up
curl http://localhost:8000/...
```

---

## 4. Lab Structure

```text
labs/<step>/
├── lab-01-<n>/
├── lab-02-<n>/
└── shared/
```

Each lab is isolated. Shared utilities live in `shared/`.

---

## 5. Mapping to Documentation

| Documentation | Lab |
|---------------|-----|
| docs/\<step\>/\<topic\>.md | lab-01-\<n\> |
| docs/\<step\>/\<topic\>.md | lab-02-\<n\> |

---

## 6. Validation

Expected outputs and behaviors for each lab.

```text
Input: "What is RAG?"
Expected: Response uses retrieved context
```

---

## 7. Common Issues

Typical problems: environment not running, missing dependencies, incorrect API usage, model not loaded.

---

## 8. Engineering Notes

Performance considerations, limitations of local runtime, expected behavior under load.

---

## 9. Next Steps

What to explore next, which docs to revisit, and how labs evolve across the module.
