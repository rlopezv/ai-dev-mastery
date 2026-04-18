# STEP README TEMPLATE

## Purpose

This document defines the **entry point for a step**.

It applies to:

```text id="z9r9l0"
docs/<step>/README.md
```

The step README is responsible for:

* defining scope
* introducing key concepts
* positioning the step in the roadmap
* guiding navigation
* connecting documentation with labs

It is **orientational**, not a deep technical explanation.

---

## Frontmatter (MANDATORY)

```yaml id="e6bjjg"
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

### Goal

Provide a high-level understanding of the step.

### Must include

* what this step is about
* why it matters
* what capability it unlocks

---

## 2. Scope

### Goal

Define boundaries clearly.

### Must include

* what is covered
* what is NOT covered

---

## 3. Key Concepts

### Goal

List the core ideas of the step.

### Format

```text id="o9r9hm"
- concept-1
- concept-2
- concept-3
```

### Rules

* Must be concise
* Must align with topic files
* Must NOT duplicate full explanations

---

## 4. Concept Map (HIGHLY RECOMMENDED)

### Goal

Show relationships between concepts.

### Format

* diagram (preferred)
* structured list (fallback)

### Example

```text id="fhk53l"
LLM → Prompt → Tools → RAG → Memory → Agents
```

---

## 5. Learning Flow

### Goal

Explain how to approach the step.

### Must include

* order of topics
* dependencies between topics

---

## 6. Documentation Structure

### Goal

Show what exists in the step.

### Format

```text id="0p4nkp"
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

### Goal

Explain what labs exist and why.

### Must include

* types of labs
* what they demonstrate

### Example

| Lab    | Purpose        |
| ------ | -------------- |
| lab-01 | observation    |
| lab-02 | implementation |

---

## 8. How to Use This Step

### Goal

Guide the reader.

### Must include

* recommended path
* optional paths (if any)

---

## 9. Relationship to Other Steps

### Goal

Position the step in the roadmap.

### Must include

* what comes before
* what comes after

---

## 10. Next Steps

### Goal

Guide continuation.

### Must include

* direct link to next step or topics

---

# Structural Rules

This document MUST:

* include frontmatter
* define scope explicitly
* list key concepts
* describe structure
* include labs overview

This document MUST NOT:

* behave like a topic file
* include deep explanations
* duplicate content from topic documents

---

# Writing Rules

This document SHOULD:

* be concise and structured
* focus on navigation and orientation
* avoid deep technical detail
* prioritize clarity over completeness

This document MUST NOT:

* introduce complex explanations
* include unnecessary theory

---

# Validation Expectations

Validated using:

```text id="l2q09f"
meta/standards/validation/docs-checklist.md
```

Critical checks:

* SC-1 (frontmatter)
* SC-3 (structure present)
* CQ-3 (scope completeness)
* PQ-1 (progression clarity)
* IQ-5 (roadmap alignment)

---

# Review Expectations

Reviewed using:

```text id="bl5y3u"
meta/standards/review/review-protocol.md
```

Focus:

* clarity of scope
* correctness of positioning
* coherence with topics
* usefulness as entry point

---

# Final Rule

A step README is valid only if:

* it clearly defines the step
* it guides navigation effectively
* it aligns with the roadmap
* it does NOT attempt to teach in depth

Otherwise:

```text id="wrb0zk"
STEP README = NOT ACCEPTABLE
```
