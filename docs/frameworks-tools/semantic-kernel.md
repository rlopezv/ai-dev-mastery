---
id: "frameworks-tools-semantic-kernel"
title: "Semantic Kernel"
type: "topic"
step: "frameworks-tools"
path: "docs/frameworks-tools/semantic-kernel.md"
status: "draft"
level: "intermediate"

concepts:
  - "Semantic Kernel"
  - "kernel"
  - "plugin"
  - "planner"
  - "semantic function"
  - "native function"

prerequisites:
  - "docs/structured-outputs/tool-usage.md"
  - "docs/frameworks-tools/langchain.md"

next:
  - "docs/frameworks-tools/framework-comparison.md"

related:
  - "docs/ai-agents/agent-patterns.md"
  - "docs/frameworks-tools/autogen.md"
  - "docs/frameworks-tools/framework-comparison.md"

implementation_refs:
  - "labs/frameworks-tools/lab-semantic-kernel"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Explains how Semantic Kernel's kernel, plugin, and planner model integrates AI capabilities into enterprise applications and when this architecture is the right choice."
---

## 1. Intuition

Semantic Kernel (SK) organizes AI capabilities as a service registry. The **kernel** is a
central object that holds model connections, memory stores, and plugin registrations. A
**plugin** is a named collection of functions — each function is either a prompt template
(**semantic function**) or a Python/C# method (**native function**). When a task requires
multiple functions, a **planner** determines which functions to call and in what order,
without the developer writing the orchestration logic.

The analogy for enterprise Java architects: the kernel is the Spring application context.
Plugins are Spring beans. Semantic functions are declarative — configuration-driven.
Native functions are imperative — code. The planner is a dependency injector that wires
them at runtime based on a task description.

---

## 2. Explanation

### 2.1 Why

Enterprise applications integrate AI capabilities into existing systems — CRM, ERP, HR
platforms — that were not built with LLMs in mind. Each AI capability is a function: a
prompt that classifies support tickets, a function that queries a database, a native
function that formats a response in a corporate template. The challenge is composing these
functions into workflows without coupling them to each other.

Semantic Kernel was designed to solve this composition problem for enterprise teams. By
registering all AI and non-AI functions into a single kernel and delegating composition
to a planner, it allows new workflows to be assembled from existing building blocks
without modifying the blocks themselves.

### 2.2 How

**The Kernel** is instantiated once and configured with an AI service (OpenAI, Azure
OpenAI, Anthropic, Ollama) and optional memory store. All functions are registered against
the kernel, and all invocations go through it.

**Semantic Functions** are prompt templates stored as text with a companion YAML
configuration that declares the function's name, description, input variables, and
execution settings. SK renders the template with provided variables and submits it to the
configured AI service. The description is what makes the function discoverable by the
planner.

**Native Functions** are Python methods decorated with `@kernel_function`. They accept
typed arguments and return typed results. The decorator registers the function's name and
description with the kernel, making it available to the planner alongside semantic
functions.

**Plugins** group related functions under a namespace. A `CustomerPlugin` might contain
`get_customer_details` (native) and `summarize_customer_history` (semantic). Plugins are
registered with `kernel.add_plugin`.

**Planners** generate execution plans from a task description and the set of registered
functions. `FunctionChoiceBehavior` is the standard planner: it presents all registered
functions to the model as tools and lets the model decide which ones to call, in what
order, and with what arguments. The kernel executes each function call and feeds the
result back to the model.

### 2.3 Code example

```python
# See: labs/frameworks-tools/lab-semantic-kernel/main.py
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function

kernel = Kernel()
kernel.add_service(OpenAIChatCompletion(service_id="default", ai_model_id="gpt-4o-mini"))

class WeatherPlugin:
    @kernel_function(name="get_weather", description="Returns current weather for a city")
    def get_weather(self, city: str) -> str:
        return f"Weather in {city}: 22°C, partly cloudy."

kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")

async def main():
    result = await kernel.invoke_prompt(
        "What is the weather in {{$city}}?", city="Madrid"
    )
    print(result)

asyncio.run(main())
```

---

## 3. Table

| Component | Role | Declared as |
|-----------|------|-------------|
| `Kernel` | Central registry and executor | instantiated object |
| AI Service | LLM connection | `kernel.add_service(...)` |
| Semantic Function | Prompt template with description | YAML config + text file, or inline |
| Native Function | Python method with description | `@kernel_function` decorator |
| Plugin | Named collection of functions | `kernel.add_plugin(...)` |
| Planner (`FunctionChoiceBehavior`) | Selects and sequences functions for a task | chat execution settings |
| Memory Store | Contextual memory backend | `kernel.add_memory_store(...)` |

---

## 4. Engineering Implications

**Function descriptions drive planner quality.** The planner selects functions based on
their text descriptions. A vague description ("does some processing") causes the planner
to skip the function or misapply it. Write function descriptions as precise capability
statements: "Returns the total purchase amount for a customer ID in the last 30 days."

**The kernel is a mutable global state container.** Adding a plugin or replacing an AI
service mutates the kernel. In multi-tenant applications where different request contexts
require different configurations, sharing a single kernel instance requires careful
synchronization. Consider per-request kernels for isolation.

**Semantic function templates are external configuration.** Prompt templates stored as
files can be versioned, deployed, and updated independently of application code. This is a
significant advantage for enterprise teams that need to update prompts without
redeploying services — but requires a deployment pipeline for the template files.

**Async-first API.** Semantic Kernel's Python SDK is async throughout. All function
invocations are coroutines. Applications must integrate with an async runtime
(`asyncio`) to use SK, which can be a friction point when integrating with synchronous
frameworks.

---

## 5. Implementation Connection

`lab-semantic-kernel` builds an application with three registered plugins — a native data
plugin, a semantic summarization function, and a formatting function — and uses the
`FunctionChoiceBehavior` planner to orchestrate a multi-step task. Key observations:

- How the planner reads function descriptions and constructs an execution plan
- How native function return values flow into the next prompt as context
- How replacing the AI service in `kernel.add_service` is the only change needed to
  switch from OpenAI to Azure OpenAI

---

## 6. Failure Modes and Limitations

**Planner hallucination.** When the planner cannot find a registered function that
satisfies the task, it may hallucinate function names or arguments. Guard against this by
validating function calls against the registered plugin inventory before execution.

**Template file drift.** Semantic functions stored as external files can fall out of sync
with the native functions they depend on. A semantic function that references a native
function's output by an old variable name fails silently — the variable resolves to an
empty string. Treat template files as versioned artifacts and test them in CI.

**Plugin namespace collisions.** Two plugins registered under the same name overwrite each
other silently. Name plugins with explicit domain prefixes in production: `CRM_Customer`,
not `Customer`.

---

## 7. Summary

Semantic Kernel organizes AI capabilities as a registry of named functions grouped into
plugins and composed by a planner. The kernel is the central execution engine: it holds
the AI service connection, the plugin registry, and the memory store, and routes all
invocations through a unified interface. The planner assembles multi-step workflows at
runtime from registered functions without explicit orchestration code. This architecture
is well-suited for enterprise teams that need to integrate AI capabilities into existing
service-oriented systems and want to version and deploy prompt templates independently of
application code.
