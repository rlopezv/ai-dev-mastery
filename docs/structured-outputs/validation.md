---
id: "structured-outputs-validation"
title: "Structured Outputs — Validation"
type: "validation"
step: "structured-outputs"
path: "docs/structured-outputs/validation.md"
status: "draft"
level: "intermediate"

concepts:
  - "structured-output"
  - "tool-use"
  - "tool-patterns"
  - "json-schema"
  - "pydantic-model"

prerequisites:
  - "docs/structured-outputs/implementation-reference.md"

next:
  - "docs/rag/README.md"

related:
  - "docs/structured-outputs/README.md"

implementation_refs:
  - "labs/structured-outputs/"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"
  - "meta/standards/validation/labs-checklist.md"

summary: "Defines conceptual, practical, lab, and integration validation criteria for the structured-outputs step."
---

# Structured Outputs — Validation

## Navigation

[Docs](../README.md) / [Structured Outputs](README.md) / Structured Outputs — Validation

---

## 1. Validation Overview

After completing this step, the learner should be able to:

- Explain the difference between prompt-only JSON format instructions and API-level schema enforcement, and describe the failure modes of each.
- Implement the complete tool use cycle: declare a tool, detect a tool call, execute it, return the result, and handle the final response.
- Identify which tool pattern (single, parallel, sequential, router) applies to a given problem and implement the corresponding loop structure.
- Design a Pydantic schema that is reliable on partial or adversarial inputs by using enums, optional fields, and bounded types.

Mastery is practical: the learner can build a working structured output or tool use integration, not just describe the concepts.

---

## 2. Conceptual Validation

| Concept | Validation Method |
|---------|------------------|
| Structured output | Explain the difference between JSON mode and response-format schema enforcement; state what each guarantees and what it does not |
| Tool use | Describe all four phases of the tool call cycle (declaration, model call, execution, result return) without referring to the docs |
| Function calling | Given an OpenAI API response, identify the `finish_reason` value that signals a tool call; locate `tool_calls[0].function.arguments` in the response |
| JSON Schema | Write a JSON Schema or Pydantic model for a given data structure with at least one enum, one integer with bounds, and one optional field |
| Tool patterns | Given a description of a multi-tool scenario, identify the correct pattern (parallel vs sequential vs router) and justify the choice |
| Provider differences | State the schema differences between OpenAI and Anthropic tool use (role name for result, argument format, finish reason value) |
| Schema design | Explain why `Literal["a", "b"]` produces more reliable output than `str` for a categorical field |

---

## 3. Practical Validation

```text
Task: Implement a structured extraction pipeline
Input: Unstructured customer support ticket text
Output: A typed Python object with: severity (enum), affected_component (str),
        requires_follow_up (bool), estimated_resolution_days (int | None)
Expected:
  - Pydantic model declared as the response format
  - response.choices[0].message.parsed returns the typed object (not None)
  - All required fields populated; optional field returns None when absent from input
  - No manual json.loads() call
```

```text
Task: Implement a tool use loop with two independent tools
Tools: get_stock_price(ticker: str) → str, get_company_info(ticker: str) → str
Query: "Give me a summary of AAPL: current price and what the company does."
Expected:
  - Both tools declared in the tools list
  - First response has finish_reason == "tool_calls" with two entries in tool_calls
  - Both results appended before the next model call
  - Final response incorporates both results
  - No IndexError when accessing tool_calls (iterate, do not index [0])
```

```text
Task: Implement a sequential chain
Pipeline: geocode a city name → fetch weather using lat/lon
Expected:
  - Two separate API calls with expanding message history
  - Output of step 1 (lat/lon) is passed as input to step 2
  - No model involvement in step ordering — application drives the pipeline
```

---

## 4. Lab Validation

| Lab | Validation Criteria |
|-----|---------------------|
| `lab-structured-outputs` | Three observations run: prompt-only (shows failure), JSON mode, schema enforcement. Parse success rate improves with each. `message.parsed` returns a typed object in observation 3. |
| `lab-tool-usage` | Full tool call cycle completes. `finish_reason` is `"tool_calls"` on the first response and `"stop"` on the second. The tool executes with the correct arguments. Anthropic path shows schema differences. |
| `lab-tool-patterns` | All four patterns run. Parallel pattern shows `len(msg.tool_calls) > 1`. Sequential chain logs each step. Router selects the correct tool for each query in a multi-query test. |
| `lab-schema-design` (optional) | Constrained schema achieves higher accuracy than unconstrained baseline on adversarial inputs. Optional fields return `None` rather than hallucinated values when information is absent. |

---

## 5. Integration Validation

**Schema enforcement + tool use.** The learner can explain that both structured output enforcement and tool use rely on JSON Schema declarations, and that tool parameter schemas follow the same design principles as response format schemas.

**Tool use as the Anthropic structured output path.** The learner can describe that Anthropic does not have a dedicated JSON mode — structured output is achieved by declaring a tool with the target schema and using `tool_choice="required"` or equivalent.

**Connection to prompt-engineering.** The learner can explain the relationship between prompt-side output format specification (prompt-engineering module) and API-level schema enforcement (this module): prompt specification is best-effort; schema enforcement is a guarantee. Both may be combined — the system prompt can still describe the desired format, and the schema provides the enforcement.

**Connection to ai-agents.** The learner can trace how the tool use loop in this module extends to agent loops: the same cycle (generate → call → execute → return) repeats with persistence (conversation history) and planning (the model chooses the next tool based on accumulated results).

---

## 6. Failure Detection

**Skipping the finish-reason check.** The learner accesses `message.tool_calls[0]` without checking `finish_reason`. The correct pattern gates on `finish_reason == "tool_calls"` first.

**Single-indexing parallel tool calls.** The learner writes `msg.tool_calls[0]` and misses additional calls when the model emits multiple tool calls. The correct pattern iterates the full `tool_calls` list.

**Forgetting to append the assistant message.** The learner appends tool result messages without first appending the assistant message containing the tool calls. The provider rejects the request because `tool_call_id` values have no corresponding calls in the history.

**Using `required` for all fields.** The learner declares all fields as required and observes hallucinated values when input is partial. The correction is to make absent-able fields optional with `= None` defaults.

**Treating arguments as a dict.** OpenAI's `tool_call.function.arguments` is a JSON string, not a dict. The learner must call `json.loads()` before passing to the function. Anthropic's `tool_use.input` is already a dict — this difference trips up learners who switch between providers without normalizing.

---

## 7. Completion Criteria

This step is complete when:

- All three core topics (`structured-outputs.md`, `tool-usage.md`, `tool-patterns.md`) can be explained without reference to the documents.
- `lab-structured-outputs`, `lab-tool-usage`, and `lab-tool-patterns` execute and produce expected output.
- The learner can implement a two-tool parallel loop from a blank file without consulting the lab code.
- The learner can design a Pydantic schema for an arbitrary extraction task and justify field choices (required vs optional, enum vs string, bounded vs unbounded).
- The learner can identify which tool pattern applies given a problem description and explain the message accumulation structure for that pattern.

---

## 8. Self-Assessment Checklist

```text
Conceptual
- [ ] I can explain the difference between JSON mode and response-format schema enforcement
- [ ] I can describe the four phases of the tool use cycle
- [ ] I can identify the correct tool pattern for a given scenario
- [ ] I can explain how Anthropic achieves structured output without a dedicated JSON mode
- [ ] I can describe the schema differences between OpenAI and Anthropic tool use

Practical
- [ ] I can declare a Pydantic model and use it as a response_format
- [ ] I can implement the finish-reason gate correctly
- [ ] I can handle a parallel tool response (iterate tool_calls, append all results)
- [ ] I can hard-code a sequential chain pipeline
- [ ] I can declare multiple tools for a router pattern

Labs
- [ ] lab-structured-outputs runs and shows the parse success improvement across three observations
- [ ] lab-tool-usage completes the full cycle: declare → call → execute → return → final response
- [ ] lab-tool-patterns runs all four patterns and shows round-trip count differences
- [ ] lab-schema-design (optional) shows constrained schema outperforming unconstrained baseline
```

---

## 9. Next Steps

**If validation fails:**
- Re-read `tool-usage.md` section 2.2 (the four phases) and trace the code example manually.
- Run `lab-tool-usage` step by step, printing the message list after each append to observe the growing history.
- Re-read `schema-design.md` section 2.2 on field selection and constraint types.

**If validation passes:**
- Proceed to `docs/rag/README.md`.
- Note that RAG retrieval tools are a direct application of the tool use cycle — retrieval is a tool the model calls to fetch relevant context.
- The tool patterns from this step (particularly sequential chain and parallel tools) recur in RAG pipeline construction.
