# architecture-scaffold.md

## Frontmatter (MANDATORY)

```yaml
---
id: "<step>-architecture"
title: "<Step Name> — Architecture"
type: "architecture"
step: "<NN-step-name>"
path: "docs/<NN-step-name>/architecture.md"
status: "draft"
level: "intermediate"

concepts:
  - "<system-component-1>"
  - "<system-component-2>"

prerequisites:
  - "docs/<step>/README.md"

next:
  - "docs/<step>/implementation-reference.md"

related:
  - "<topic-1>"
  - "<topic-2>"

implementation_refs:
  - "labs/<step>/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes how components interact within this step."
---
```

---

# Architecture

## Navigation

[Docs](../README.md) / [<Module Name>](README.md) / Architecture

---

## 1. System Overview

What system is being described, what problem it solves, and its main components.

---

## 2. Core Components

| Component | Role | Responsibility |
|-----------|------|----------------|
| \<name\> | \<role\> | \<what it does\> |

---

## 3. Component Interactions

How components work together: data flow, control flow, dependencies.

---

## 4. Data Flow (MANDATORY)

How data moves through the system: inputs → transformations → outputs.

```text
User input → Prompt → LLM → Response
```

---

## 5. Execution Flow

Sequence of operations at runtime, including decision points and loops.

---

## 6. Integration Points

How the system connects to other steps, external services, and labs.

---

## 7. Trade-offs and Design Decisions

Why this design is chosen, alternatives considered, and trade-offs accepted.

---

## 8. Mapping to Labs

| Component | Lab |
|-----------|-----|
| \<component\> | lab-01 |
| \<component\> | lab-02 |

---

## 9. Limitations and Boundaries

What the architecture does NOT cover and constraints of the approach.

---

## 10. Summary

Key components, key interactions, and system purpose restated concisely.
