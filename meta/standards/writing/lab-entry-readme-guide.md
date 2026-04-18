# LAB README TEMPLATE

## Purpose

This document defines the **entry point for labs within a step**.

It is used in:

```text
labs/<step>/README.md
```

Its purpose is to:

* explain how to run labs
* define what is implemented
* connect labs with documentation
* provide execution guidance

This document is **operational**, not purely pedagogical.

---

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
  - "labs/<step>/lab-01-<name>"
  - "labs/<step>/lab-02-<name>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how to run and understand the labs for this step."
---
```

---

## 1. Overview

### Purpose of the labs

Explain:

* what these labs implement
* why they exist in this step

### Scope

Clarify:

* what is covered
* what is NOT covered

---

## 2. Lab Inventory

List all labs in the step.

| Lab           | Description            | Type                         |
| ------------- | ---------------------- | ---------------------------- |
| lab-01-<name> | <what it demonstrates> | observation / implementation |
| lab-02-<name> | <what it builds>       | implementation               |

### Rules

* Must include ALL labs
* No empty entries
* Each lab must be meaningful

---

## 3. Execution Model

Explain how labs are executed.

### Runtime

* docker-compose usage
* services involved (e.g. FastAPI, Ollama, vector DB)

### Entry points

* API endpoints
* scripts
* CLI commands

### Example

```bash
docker-compose up
curl http://localhost:8000/...
```

---

## 4. Lab Structure

Explain how labs are organized.

```text
labs/<step>/
├── lab-01-<name>/
├── lab-02-<name>/
└── shared/
```

### Rules

* Each lab is isolated
* Shared utilities live in `shared/`

---

## 5. Mapping to Documentation

Explain how labs relate to docs.

| Documentation          | Lab           |
| ---------------------- | ------------- |
| docs/<step>/<topic>.md | lab-01-<name> |
| docs/<step>/<topic>.md | lab-02-<name> |

### Rule

Every lab must map to at least one document.

---

## 6. Validation

Explain how to validate labs.

### Functional validation

* expected API responses
* expected outputs

### Behavioral validation

* what should happen
* what should NOT happen

### Example

```text
Input: "What is RAG?"
Expected: Response uses retrieved context
```

---

## 7. Common Issues

List typical problems.

* environment not running
* missing dependencies
* incorrect API usage
* model not loaded

---

## 8. Engineering Notes

Explain relevant engineering constraints.

* performance considerations
* limitations of local runtime
* expected behavior under load

---

## 9. Next Steps

Guide the user:

* what to explore next
* which docs to revisit
* how labs evolve

---

## Structural Rules

This document MUST:

* include complete frontmatter
* list all labs
* include execution instructions
* map labs to documentation
* define validation approach

This document MUST NOT:

* act as a conceptual deep-dive
* replace documentation
* contain incomplete instructions

---

## Writing Rules

This document SHOULD:

* be concise and operational
* avoid abstract explanations
* focus on execution and behavior
* use examples where necessary

It SHOULD NOT:

* duplicate content from docs
* introduce new theoretical concepts
