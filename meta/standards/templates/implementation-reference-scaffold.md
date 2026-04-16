# implementation-reference-scaffold.md

## Scope

This document bridges concepts and architecture to implementation patterns.
It answers: **"Why is the code structured this way?"**

It does NOT answer: "How do I set up the environment?" or "How do I run the labs?"
That content belongs in `labs/<module>/README.md`.

Concretely:
- No setup commands (`ollama serve`, `pip install`, `docker-compose up`)
- No troubleshooting for environment issues (service not running, model not found)
- No instructions for running individual labs
- Failure modes must be design-level (wrong pattern choice, wrong assumption)
  — not operational (dependency missing, port not open)

---

## Frontmatter (MANDATORY)

```yaml
---
id: "<module>-implementation-reference"
title: "<Module Name> — Implementation Reference"
type: "implementation-reference"
step: "<module-name>"
path: "docs/<module-name>/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "<component-1>"
  - "<pattern-1>"

prerequisites:
  - "docs/<module-name>/architecture.md"

next:
  - "docs/<module-name>/validation.md"

related:
  - "<topic-1>"
  - "<topic-2>"

implementation_refs:
  - "labs/<module-name>/lab-<n>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how concepts and architecture translate into implementation patterns."
---
```

---

## 1. Implementation Overview

How the architecture components map to concrete tools and interfaces.
Relationship to the concept docs and the architecture doc.

> **Note:** This document contains orientative code — structures, interfaces, signatures.
> It is not directly executable. For complete, runnable implementations see the labs
> referenced in `implementation_refs`.

---

## 2. Core Patterns

| Pattern | Description | When to use |
|---------|-------------|-------------|
| `<pattern>` | `<what it does>` | `<use case>` |

---

## 3. Component Mapping

| Architecture Component | Implementation |
|------------------------|----------------|
| `<component>` | `<module / class / function>` |

---

## 4. Data Structures and Interfaces

Key inputs, outputs, and intermediate representations.

```python
# Orientative — see labs/<module-name>/lab-<n>/main.py for full implementation
```

---

## 5. Design Decisions

Why each pattern is the right abstraction for its component.
Why this tool was chosen over alternatives.
Why the code is structured as it is — not how to run it.

---

## 6. External Dependencies

Table only. No setup commands — those belong in `labs/<module>/README.md`.

| Tool | Role | Infrastructure profile |
|------|------|------------------------|
| Ollama | LLM runtime | `light` |
| ChromaDB | Vector store | `full` |

---

## 7. Mapping to Labs (MANDATORY)

| Pattern / Component | Lab | Concept verified |
|---------------------|-----|-----------------|
| `<pattern>` | `lab-<n>` | `<what the lab confirms>` |

---

## 8. Trade-offs and Constraints

Design-level trade-offs: accuracy vs cost, precision vs simplicity, one tool vs another.
Not performance tips or hardware requirements.

---

## 9. Failure Modes

Design-level mistakes: wrong pattern for the task, incorrect assumptions about the interface,
misuse of a data structure. Not environment issues — those belong in `labs/<module>/README.md`.

---

## 10. Summary

Key patterns, components, and the design decisions that connect them.
