# reference-architecture-scaffold.md

## Frontmatter (MANDATORY)

```yaml
---
id: "reference-architectures-<architecture-name>"
title: "<Architecture Name>"
type: "reference-architecture"
step: "reference-architectures"
path: "docs/reference-architectures/<architecture-name>.md"
status: "draft"
level: "advanced"

concepts:
  - "<pattern-1>"
  - "<component-1>"

prerequisites:
  - "<module that introduces the core pattern>"

next:
  - "<related reference architecture>"

related:
  - "<topic from another module>"

implementation_refs:
  - "labs/reference-architectures/lab-<n>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "<One-sentence description of the system this architecture represents>"
---
```

---

## Navigation

[Docs](../../README.md) / <Architecture Name>

---

## 1. Problem Statement

What problem does this architecture solve. Who needs it and in what context.

---

## 2. Architecture Overview

High-level description of the system. Include a diagram or structured representation.

```text
[Component A] → [Component B] → [Component C]
                     ↓
              [Component D]
```

---

## 3. Components

| Component | Role | Technology (example) |
|-----------|------|----------------------|
| `<name>` | `<what it does>` | `<Ollama / ChromaDB / FastAPI / ...>` |

---

## 4. Data Flow

Step-by-step description of how data moves through the system at runtime.

---

## 5. Pattern Map

Which patterns from previous modules appear in this architecture and how they combine.

| Pattern | Origin module | Role in this architecture |
|---------|---------------|---------------------------|
| `<pattern>` | `<module>` | `<how it is used here>` |

---

## 6. Design Decisions

Key decisions made in this architecture and the trade-offs they imply.

| Decision | Alternative | Reason |
|----------|-------------|--------|
| `<decision>` | `<alternative>` | `<why>` |

---

## 7. Variants and Extensions

Known variants of this architecture and when to choose them.

---

## 8. Limitations and Failure Modes

What this architecture does not handle well. Operational risks and boundary conditions.

---

## 9. Related Architectures

Links to other reference architectures in this module that share patterns or components.
