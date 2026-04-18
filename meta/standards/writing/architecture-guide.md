# ARCHITECTURE TEMPLATE

## Purpose

This document defines the **system-level view for a step**.

It applies to:

```text id="3j3k9a"
docs/<step>/architecture.md
```

The architecture document is responsible for:

- describing how components interact
- defining system structure within the step
- connecting concepts into a coherent system
- preparing the reader for implementation and labs

It is **system-oriented**, not concept-oriented.

---

## Frontmatter (MANDATORY)

```yaml id="q0s2v1"
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

## 1. System Overview

### Goal

Provide a high-level understanding of the system.

### Must include

- what system is being described
- what problem it solves
- main components involved

---

## 2. Core Components

### Goal

Define the building blocks of the system.

### Format

| Component | Role   | Responsibility |
| --------- | ------ | -------------- |
| <name>    | <role> | <what it does> |

### Rules

- Each component must be clearly defined
- No vague components (e.g. "system", "AI")

---

## 3. Component Interactions

### Goal

Explain how components work together.

### Must include

- data flow
- control flow
- dependencies

### Format

- step-by-step flow OR
- diagram (preferred)

---

## 4. Data Flow (MANDATORY)

### Goal

Describe how data moves through the system.

### Must include

- inputs
- transformations
- outputs

### Example

```text id="n1ql82"
User input → Prompt → LLM → Response
```

---

## 5. Execution Flow

### Goal

Describe runtime behavior.

### Must include

- sequence of operations
- decision points
- loops or iterations

---

## 6. Integration Points

### Goal

Show how the system connects to:

- other steps
- external services
- labs

### Must include

- APIs
- tools
- runtime dependencies

---

## 7. Trade-offs and Design Decisions

### Goal

Explain architectural choices.

### Must include

- why this design is chosen
- alternatives (if relevant)
- trade-offs

---

## 8. Mapping to Labs

### Goal

Connect architecture to implementation.

### Must include

- which labs implement which components
- what each lab demonstrates

### Format

| Component   | Lab    |
| ----------- | ------ |
| <component> | lab-01 |
| <component> | lab-02 |

---

## 9. Limitations and Boundaries

### Goal

Define scope limits.

### Must include

- what the architecture does NOT cover
- constraints of the approach

---

## 10. Summary

### Goal

Reinforce system understanding.

### Must include

- key components
- key interactions
- system purpose

---

# Structural Rules

This document MUST:

- describe a system (not isolated concepts)
- include component breakdown
- include data flow
- include execution flow
- include mapping to labs

This document MUST NOT:

- behave like a topic file
- duplicate detailed explanations from topics
- omit system-level structure

---

# Writing Rules

This document SHOULD:

- prioritize clarity of relationships
- use diagrams or structured flows
- reduce ambiguity in system behavior

This document MUST NOT:

- be purely descriptive without structure
- avoid system-level explanation
- over-focus on theory

---

# Validation Expectations

Validated using:

```text id="6b4cxu"
meta/standards/validation/docs-checklist.md
```

Critical checks:

- SC-3 (structure present)
- CQ-1 (correctness)
- EQ-1 (engineering implications)
- IQ-1 (integration alignment)

---

# Review Expectations

Reviewed using:

```text id="9k22p1"
meta/standards/review/review-protocol.md
```

Focus:

- system coherence
- clarity of flows
- correctness of interactions
- completeness of architecture

---

# Final Rule

An architecture document is valid only if:

- it describes a coherent system
- it connects components explicitly
- it reflects real system behavior
- it maps to implementation

Otherwise:

```text id="k4yzt9"
ARCHITECTURE = NOT ACCEPTABLE
```
