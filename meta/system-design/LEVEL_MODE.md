# LEVEL_MODEL

## Purpose

This document defines the normative level model used across the repository. The level assigned to a module is not only a pedagogical classification. It is also an execution contract.

Each level governs:

- allowed runtime complexity
- allowed infrastructure footprint
- allowed abstraction layers
- required observability
- acceptable failure surface
- completion criteria

All modules, labs, and infrastructure decisions MUST comply with this model.

---

## Levels

The repository defines three levels:

- FOUNDATIONAL
- INTERMEDIATE
- ADVANCED

A module level MUST be explicitly declared in the root module index and MUST be consistent with its docs, labs, and runtime requirements.

---

## Global Rules

### G-1. Level is normative

A module level MUST be treated as a repository contract, not as descriptive metadata.

### G-2. Runtime must follow level policy

A module MUST NOT require runtime components or operational complexity outside the policy of its declared level.

### G-3. Infrastructure must remain explainable

All required runtime components MUST be justified by the learning objective of the module.

### G-4. Complexity must be introduced progressively

A later level MAY expand runtime complexity, but an earlier level MUST NOT anticipate complexity that belongs to a later level.

### G-5. Exceptions must be explicit

If a module uses a runtime variant that differs from the standard profile of its level, that exception MUST be documented explicitly in:
- the module README
- the labs README
- the infrastructure README

### G-6. Validation must be level-aware

A module is complete only if its validation criteria are compatible with the constraints of its level.

---

## FOUNDATIONAL

### Intent

FOUNDATIONAL modules establish first-principles understanding and direct interaction with core concepts.

The objective is concept isolation, direct observation, and minimal runtime friction.

### Runtime Policy

FOUNDATIONAL modules MUST use a minimal runtime envelope.

They MUST:
- use a single primary runtime context
- minimize moving parts
- prefer direct interaction with the model or API
- keep execution flow explicit and inspectable

They MUST NOT require:
- multi-service orchestration
- persistent storage
- vector databases
- agent runtimes
- framework-heavy abstraction
- deployment-like infrastructure

### Infrastructure Policy

FOUNDATIONAL modules SHOULD run with the lightest repository-supported profile.

They SHOULD require only:
- local LLM runtime
- optional local UI for manual inspection

They MUST NOT depend on external stateful services.

### Abstraction Policy

FOUNDATIONAL modules MUST prefer:
- raw APIs
- minimal wrappers
- explicit request/response handling
- explicit parsing and validation where relevant

They MUST NOT hide core behavior behind framework conventions.

### Observability Policy

FOUNDATIONAL modules MUST expose:
- input
- output
- key parameters
- immediate behavior under change

The learner MUST be able to see what changed and why.

### Failure Policy

FOUNDATIONAL modules MUST minimize setup-related failure modes.

They SHOULD favor:
- deterministic or near-deterministic exercises
- small, isolated labs
- short feedback loops

Troubleshooting burden MUST remain low.

### Definition of Done

A FOUNDATIONAL module is complete only if:
- the core concept is demonstrated in isolation
- the runtime setup is minimal
- the learner can inspect the main inputs and outputs directly
- the labs are reproducible with low operational friction
- no forbidden runtime components are required

### Forbidden in FOUNDATIONAL

The following are prohibited unless the module is reclassified:
- vector databases
- persistent memory stores
- multi-agent runtimes
- orchestration frameworks that hide control flow
- deployment or observability stacks
- infrastructure that introduces non-essential operational burden

---

## INTERMEDIATE

### Intent

INTERMEDIATE modules introduce composition.

The objective is to connect concepts into working AI subsystems while keeping the runtime understandable and bounded.

### Runtime Policy

INTERMEDIATE modules MAY use multi-component runtimes when those components are required by the module objective.

They MAY include:
- vector databases
- persistent local storage
- tool execution
- retrieval pipelines
- controlled multi-step flows
- selected framework usage

They MUST:
- keep component boundaries visible
- keep data flow explainable
- justify each additional runtime component

They MUST NOT introduce production-grade operational complexity unless that complexity is the point of the module.

### Infrastructure Policy

INTERMEDIATE modules MAY require a richer runtime than FOUNDATIONAL.

They MAY use:
- local vector stores
- multiple local services
- richer dependency sets

They SHOULD remain runnable in a controlled local environment.

They MUST NOT require a production deployment model.

### Abstraction Policy

INTERMEDIATE modules MAY use abstractions, but those abstractions MUST NOT obscure the core mechanism being taught.

When frameworks are used, the module MUST still make visible:
- what the framework is doing
- what problem it solves
- what the underlying primitives are

### Observability Policy

INTERMEDIATE modules MUST expose:
- component boundaries
- data flow between components
- failure points at the integration layer
- where state is stored and retrieved

### Failure Policy

INTERMEDIATE modules MAY include controlled integration failures.

The learner MAY be expected to debug:
- configuration mismatches
- schema mismatches
- retrieval failures
- tool execution errors
- state handling mistakes

Failure handling MUST remain bounded and teachable.

### Definition of Done

An INTERMEDIATE module is complete only if:
- the subsystem works end to end in a controlled local environment
- runtime components are justified by the module objective
- control flow remains understandable
- the labs demonstrate integration, not just isolated concepts
- observability is sufficient to debug the main failure cases

### Forbidden in INTERMEDIATE

The following are prohibited unless explicitly justified:
- black-box framework usage without explaining underlying behavior
- unnecessary service sprawl
- production-scale deployment complexity
- hidden stateful dependencies
- implicit infrastructure requirements not documented in the module and infra docs

---

## ADVANCED

### Intent

ADVANCED modules address system-level engineering concerns.

The objective is not only to build AI functionality, but to evaluate, operate, optimize, govern, and architect it under realistic constraints.

### Runtime Policy

ADVANCED modules MAY use full system runtimes.

They MAY include:
- multi-service setups
- deployment-oriented configurations
- observability stacks
- evaluation pipelines
- performance optimization layers
- architecture-level integration patterns

Runtime complexity is allowed only when it contributes directly to the module objective.

### Infrastructure Policy

ADVANCED modules MAY require:
- full local runtime
- extended service composition
- operational tooling
- evaluation or monitoring infrastructure

They SHOULD still provide a bounded local-first path when feasible.

### Abstraction Policy

ADVANCED modules MAY use higher-level abstractions and frameworks.

They MUST make trade-offs explicit:
- convenience vs control
- velocity vs transparency
- abstraction vs debuggability
- local simplicity vs production realism

### Observability Policy

ADVANCED modules MUST provide system-level visibility.

They SHOULD address:
- logs
- metrics
- traces
- evaluation outputs
- operational signals
- failure analysis

### Failure Policy

ADVANCED modules MAY expose realistic failure surfaces.

Failure analysis is part of the learning objective.

The module MUST define what kinds of failures are in scope and how they are evaluated.

### Definition of Done

An ADVANCED module is complete only if:
- system behavior is assessed under realistic constraints
- runtime architecture is justified and documented
- evaluation or operational criteria are defined
- trade-offs are explicit
- the learner can reason about architecture, not just run a demo

### Forbidden in ADVANCED

The following are prohibited:
- unjustified architectural complexity
- runtime expansion without clear engineering value
- operational tooling added without explicit learning purpose

---

## Standard Runtime Profiles by Level

These are repository-level defaults.

### FOUNDATIONAL
Default profile:
- foundational

Expected services:
- local LLM runtime
- optional local UI

### INTERMEDIATE
Default profile:
- foundational or intermediate, depending on subsystem needs

Expected services may include:
- local LLM runtime
- local UI
- local vector storage
- controlled auxiliary services

### ADVANCED
Default profile:
- advanced

Expected services may include:
- multi-service local stack
- evaluation infrastructure
- observability tooling
- deployment-oriented components

---

## Exception Model

A module MAY declare an exception to the default runtime profile only if all of the following are true:

- the exception is required by the learning objective
- the exception does not violate the level intent
- the exception is explicitly documented
- the exception is reflected consistently in docs, labs, and infrastructure documentation

Exception declarations MUST include:
- reason
- added component(s)
- operational impact
- why the default profile is insufficient

---

## Validation Questions

Each module SHOULD be checked against the following questions:

1. Does the runtime complexity fit the declared level?
2. Are all required components justified by the learning objective?
3. Is the abstraction level appropriate for the declared level?
4. Is the observability sufficient for the learner to understand behavior?
5. Is the failure surface acceptable for the declared level?
6. Are exceptions explicitly documented and consistent across docs, labs, and infrastructure?
7. Does the module satisfy the definition of done for its level?

If any answer is no, the module MUST be revised or reclassified.