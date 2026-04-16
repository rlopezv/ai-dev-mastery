# IMPLEMENTATION REFERENCE TEMPLATE

## Purpose

This document defines the **bridge between documentation and implementation** for a step.

It applies to:

```text id="i3t7k9"
docs/<step>/implementation-reference.md
```

Its purpose is to:

- translate concepts into implementation patterns
- describe how systems are built in practice
- define implementation building blocks
- connect architecture to labs

This document is **engineering-oriented**, not purely conceptual.

---

## Frontmatter (MANDATORY)

```yaml id="k2w8m1"
---
id: "<step>-implementation-reference"
title: "<Step Name> — Implementation Reference"
type: "implementation-reference"
step: "<NN-step-name>"
path: "docs/<NN-step-name>/implementation-reference.md"
status: "draft"
level: "intermediate"

concepts:
  - "<component-1>"
  - "<pattern-1>"

prerequisites:
  - "docs/<step>/architecture.md"

next:
  - "docs/<step>/validation.md"

related:
  - "<topic-1>"
  - "<topic-2>"

implementation_refs:
  - "labs/<step>/lab-01-<name>"
  - "labs/<step>/lab-02-<name>"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how concepts and architecture translate into implementation patterns."
---
```

---

## 1. Implementation Overview

### Goal

Explain how the system is implemented in practice.

### Must include

- overall implementation approach
- how concepts translate into code
- relationship to architecture

---

## 2. Core Implementation Patterns

### Goal

Define reusable patterns.

### Format

| Pattern   | Description    | When to Use |
| --------- | -------------- | ----------- |
| <pattern> | <what it does> | <use case>  |

### Examples

- request → LLM → response
- retrieval → context → generation
- tool invocation loop

---

## 3. Component Mapping

### Goal

Map architecture → implementation.

### Format

| Architecture Component | Implementation                |
| ---------------------- | ----------------------------- |
| <component>            | <service / module / function> |

---

## 4. Data Structures and Interfaces

### Goal

Define inputs and outputs.

### Must include

- request formats
- response formats
- intermediate representations

### Example

```json id="t9v3n1"
{
  "query": "What is RAG?",
  "context": ["doc1", "doc2"]
}
```

---

## 5. Execution Flow

### Goal

Describe runtime behavior at implementation level.

### Must include

- sequence of operations
- control flow
- interaction with external systems

---

## 6. Integration with External Systems

### Goal

Explain dependencies.

### Must include

- LLM runtime (e.g. Ollama)
- vector DB (e.g. Weaviate)
- APIs / services

---

## 7. Mapping to Labs (MANDATORY)

### Goal

Connect implementation to executable artifacts.

### Format

| Pattern / Component | Lab    |
| ------------------- | ------ |
| <pattern>           | lab-01 |
| <component>         | lab-02 |

### Rules

- Every major pattern must map to at least one lab
- No orphan concepts

---

## 8. Trade-offs and Constraints

### Goal

Explain real-world limitations.

### Must include

- performance considerations
- cost implications
- complexity trade-offs

---

## 9. Failure Modes

### Goal

Expose what can go wrong in implementation.

### Must include

- incorrect usage patterns
- system failures
- boundary conditions

---

## 10. Summary

### Goal

Reinforce implementation understanding.

### Must include

- key patterns
- key components
- key flows

---

# Structural Rules

This document MUST:

- define implementation patterns
- map architecture to code
- define data structures
- include execution flow
- map to labs

This document MUST NOT:

- behave like a topic file
- stay purely conceptual
- omit real implementation details

---

# Writing Rules

This document SHOULD:

- be concrete and precise
- include structured representations
- prioritize clarity over abstraction

This document MUST NOT:

- introduce unnecessary theory
- use vague descriptions of behavior
- avoid implementation detail

---

# Validation Expectations

Validated using:

```text id="m7k4a2"
meta/standards/validation/docs-checklist.md
```

Critical checks:

- EQ-1 (engineering implications)
- CQ-1 (correctness)
- SC-3 (structure present)
- IQ-3 (implementation references)

---

# Review Expectations

Reviewed using:

```text id="v4p1x8"
meta/standards/review/review-protocol.md
```

Focus:

- correctness of implementation
- clarity of patterns
- alignment with architecture
- completeness of mapping to labs

---

# Final Rule

An implementation reference is valid only if:

- it bridges concept and execution
- it defines reusable patterns
- it connects to real labs
- it reflects real system behavior

Otherwise:

```text id="y8n2f3"
IMPLEMENTATION = NOT ACCEPTABLE
```
