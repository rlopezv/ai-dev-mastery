# TOPIC TEMPLATE

## Purpose

This document defines the **canonical structure for topic files**.

It applies to:

```text
docs/<step>/<topic>.md
```

A topic is the **primary unit of learning** in the system.

It must:

- explain a concept clearly
- connect intuition to implementation
- expose engineering implications
- be self-contained but linked to the system

---

## Frontmatter (MANDATORY)

```yaml
---
id: "<step>-<topic-name>"
title: "<Human-readable title>"
type: "topic"
step: "<NN-step-name>"
path: "docs/<NN-step-name>/<topic-name>.md"
status: "draft"
level: "foundational | intermediate | advanced"

concepts:
  - "<concept-1>"
  - "<concept-2>"

prerequisites:
  - "<step or doc>"

next:
  - "<next topic or step>"

related:
  - "<related topic>"

implementation_refs:
  - "labs/<step>/lab-<NN>-<name>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "<One-sentence explanation of the topic>"
---
```

---

## 1. Intuition

### Goal

Provide an immediate mental model.

### Requirements

- Must explain the concept in simple terms
- Must reduce abstraction
- Must NOT use heavy technical language initially

### Anti-patterns

- jumping directly into formal definitions
- assuming prior knowledge not declared in prerequisites

---

## 2. Explanation

### Goal

Explain how the concept works.

### Requirements

- Must be causal (how / why)
- Must be technically correct
- Must connect to previous knowledge

### Must include

- mechanisms
- internal behavior
- relationships between components

---

## 3. Table (MANDATORY)

### Goal

Reduce cognitive load through structured synthesis.

### Allowed table types

- comparison
- component breakdown
- input/output mapping
- trade-offs

### Requirements

- Must be meaningful (not decorative)
- Must compress information

---

## 4. Engineering Implications

### Goal

Translate concept → system behavior.

### Requirements

- Must describe how this affects system design
- Must include trade-offs when applicable
- Must reflect real-world constraints

### Examples

- performance impact
- cost considerations
- architectural decisions

---

## 5. Implementation Connection

### Goal

Bridge concept to labs.

### Requirements

- Must reference `implementation_refs`
- Must explain what the lab demonstrates
- Must describe what to observe

---

## 6. Failure Modes and Limitations

### Goal

Expose boundaries of the concept.

### Requirements

- Must include at least one limitation when applicable
- Must describe what can go wrong
- Must avoid presenting the concept as universally valid

---

## 7. Summary

### Goal

Reinforce key understanding.

### Requirements

- Must be concise
- Must restate the core idea
- Must connect to system usage

---

# Structural Rules

This document MUST:

- include all sections (1–7)
- follow the defined order
- include at least one table
- include engineering implications
- include implementation connection

This document MUST NOT:

- skip sections
- mix multiple concepts into one topic
- contain unresolved placeholders
- duplicate other topic files

---

# Writing Rules

This template MUST follow:

```text
meta/standards/writing/writing-style.md
```

Key enforcement:

- Intuition → Explanation → Table → Engineering Implication flow
- No vague language
- No purely descriptive sections
- Concepts must be grounded in behavior

---

# Validation Expectations

This document is validated using:

```text
meta/standards/validation/docs-checklist.md
```

Critical checks:

- SC-1 (frontmatter valid)
- SC-3 (structure present)
- CQ-1 (correctness)
- PQ-1 (progression)
- EQ-1 (engineering implications)

Failure to satisfy these results in rejection.

---

# Review Expectations

This document is reviewed using:

```text
meta/standards/review/review-protocol.md
```

Expected review focus:

- conceptual correctness
- pedagogical clarity
- engineering relevance
- structural completeness
- consistency across steps

---

# Final Rule

A topic is considered valid only if:

- it satisfies structure
- it passes validation scoring (≥ 8)
- it contains no critical issues
- it connects concept to implementation

Otherwise:

```text
TOPIC = NOT ACCEPTABLE
```
