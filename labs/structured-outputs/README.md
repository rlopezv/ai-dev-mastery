---
id: "structured-outputs-labs-readme"
title: "Structured Outputs — Labs"
type: "lab-readme"
step: "structured-outputs"
path: "labs/structured-outputs/README.md"
status: "draft"
level: "intermediate"

concepts:
  - "structured-output"
  - "tool-use"
  - "function-calling"
  - "tool-patterns"
  - "pydantic-model"
  - "json-schema"

prerequisites:
  - "docs/structured-outputs/implementation-reference.md"

next:
  - "labs/rag/README.md"

related:
  - "docs/structured-outputs/README.md"

implementation_refs:
  - "labs/structured-outputs/lab-structured-outputs"
  - "labs/structured-outputs/lab-tool-usage"
  - "labs/structured-outputs/lab-tool-patterns"
  - "labs/structured-outputs/lab-schema-design"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Four labs that make structured output enforcement and tool use directly observable — schema enforcement reliability, the tool call cycle, tool pattern compositions, and schema constraint design."
---

# Structured Outputs — Labs

## Navigation

[Labs](../README.md) / Structured Outputs — Labs

---


## 1. Overview

These labs implement and measure the structured output and tool use mechanisms described in `docs/structured-outputs/`. Each lab isolates one mechanism, runs it against a fixed input set, and produces measurable output that confirms the concept.

All labs run against Ollama locally using the OpenAI-compatible interface. `lab-tool-usage` additionally demonstrates the Anthropic schema path to make provider differences visible. No cloud API keys are required for the three required labs — Anthropic is optional and isolated to one observation in `lab-tool-usage`.

**Not covered:**
- Multi-agent systems where tools call other agents (see `ai-agents`)
- RAG retrieval as a tool (see `rag`)
- Evaluation of structured output quality (see `evaluation-testing`)
- Prompt design for tool use (see `prompt-engineering`)

---

## 2. Lab Inventory

| Lab | Demonstrates | Type | Required | Doc |
|-----|-------------|------|----------|-----|
| `lab-structured-outputs` | Parse reliability: prompt-only vs JSON mode vs Pydantic schema enforcement | implementation | yes | `structured-outputs.md` |
| `lab-tool-usage` | Full tool call cycle; finish-reason gate; OpenAI vs Anthropic schema | implementation | yes | `tool-usage.md` |
| `lab-tool-patterns` | Single, parallel, sequential chain, and router patterns; round-trip counts | implementation | yes | `tool-patterns.md` |
| `lab-schema-design` | Constrained vs unconstrained schema reliability on adversarial inputs | implementation | optional | `schema-design.md` |

---

## 3. Execution Model

All labs use the **`foundational` infrastructure profile**: Ollama running locally via the OpenAI-compatible interface.

**Prerequisites:**

```bash
# 1. Start Ollama
ollama serve
ollama pull llama3.2

# 2. Install dependencies
pip install -r labs/structured-outputs/requirements.txt

# 3. Configure environment
cd labs/structured-outputs
cp .env.example .env
# Edit .env if Ollama runs on a non-default URL or you want a different model
```

**Running a lab:**

```bash
cd labs/structured-outputs
python lab-structured-outputs/main.py
python lab-tool-usage/main.py
python lab-tool-patterns/main.py
python lab-schema-design/main.py     # optional
```

Each lab prints structured output to stdout. No server process is started.

---

## 4. Lab Structure

```text
labs/structured-outputs/
├── README.md                          ← this file
├── .env.example                       ← environment variable template
├── requirements.txt                   ← Python dependencies
├── shared/
│   ├── __init__.py
│   └── config.py                      ← env vars, client builders, Ollama health check
├── lab-structured-outputs/
│   ├── README.md
│   └── main.py
├── lab-tool-usage/
│   ├── README.md
│   └── main.py
├── lab-tool-patterns/
│   ├── README.md
│   └── main.py
└── lab-schema-design/
    ├── README.md
    └── main.py
```

Each lab is self-contained. The only cross-lab dependency is `shared/config.py`.

---

## 5. Mapping to Documentation

| Documentation | Lab |
|---------------|-----|
| `docs/structured-outputs/structured-outputs.md` | `lab-structured-outputs` |
| `docs/structured-outputs/tool-usage.md` | `lab-tool-usage` |
| `docs/structured-outputs/tool-patterns.md` | `lab-tool-patterns` |
| `docs/structured-outputs/schema-design.md` | `lab-schema-design` |
| `docs/structured-outputs/schema-design.md` (optional) | — (concept-only if lab not run) |

---

## 6. Validation

**lab-structured-outputs**
```
Observation 1 (prompt-only): at least one parse failure or shape mismatch
                               across 5 adversarial inputs
Observation 2 (JSON mode):    all responses parse as valid JSON;
                               shape may vary (no schema constraint)
Observation 3 (schema):       message.parsed returns typed ReviewSummary object;
                               sentiment is one of ["positive","neutral","negative"];
                               score is an integer 1–5; 0 parse failures
```

**lab-tool-usage**
```
Observation 1 (single tool):  first response finish_reason == "tool_calls";
                               tool_call.function.name == "get_current_time";
                               second response finish_reason == "stop";
                               final response mentions the time returned by the tool
Observation 2 (currency):     arguments extracted correctly (amount, from, to);
                               dispatch() returns stub result; model incorporates it
Observation 3 (Anthropic):    content block type == "tool_use";
                               input is already a dict (no json.loads needed);
                               result uses role "user" with tool_result content block
```

**lab-tool-patterns**
```
Single:      2 API round-trips (call + final)
Parallel:    2 API round-trips for 2 simultaneous tool calls;
             len(msg.tool_calls) == 2 on first response
Sequential:  3 API round-trips for 2-step pipeline;
             step 2 input contains output from step 1
Router:      correct tool selected for each of 4 query types;
             tool name printed per query
```

**lab-schema-design (optional)**
```
Constrained schema:   0 enum violations; optional fields return None
                      when absent from input; ≥80% parse success on adversarial set
Unconstrained schema: at least one field with hallucinated/guessed value
                      on inputs missing that information
```

---

## 7. Common Issues

**`message.parsed` is `None`.**
The model did not conform to the schema. This typically happens with small models (3B) on complex schemas. Simplify the schema (fewer required fields, wider enums) or switch to a 7B model via `OLLAMA_MODEL=llama3.2:7b`.

**`finish_reason` is `"stop"` instead of `"tool_calls"`.**
The model answered in text instead of calling a tool. This happens when the query does not clearly require the tool, or when the model is too small to reliably follow tool instructions. Check that `tool_choice="auto"` is set. For reliable tool invocation, use `tool_choice="required"`.

**`tool_calls` is `None` when accessed.**
Always gate access on `finish_reason == "tool_calls"`. Accessing `message.tool_calls[0]` on a non-tool response raises `TypeError`.

**`json.loads` on arguments fails.**
Some models emit malformed JSON in the `arguments` field. The labs include a guarded `json.loads` with error logging. If this happens consistently, the model is not reliably following the tool schema — try a larger model.

**Parallel tools returns only one call.**
Not all models support parallel tool calls. If `len(msg.tool_calls) == 1` in `lab-tool-patterns` observation 2, the model is emitting calls sequentially. The lab handles this correctly — two round-trips occur but pattern behavior is sequential, not parallel.

**Anthropic observation fails with `AuthenticationError`.**
Set `ANTHROPIC_API_KEY` in `.env` or skip observation 3. The Anthropic path is isolated to demonstrate schema differences — the required labs do not depend on it.

---

## 8. Engineering Notes

**Pydantic version.** The `beta.chat.completions.parse` interface requires `openai>=1.40.0` and `pydantic>=2.0.0`. The `message.parsed` attribute is populated only when `response_format` is a Pydantic model class. If using an older SDK, fall back to `json.loads(message.content)` with manual `model_validate`.

**Tool call reliability by model size.** Tool use requires the model to follow a structured calling protocol. Models below 7B parameters vary significantly in reliability. `llama3.2` (3B) handles single-tool scenarios well but may struggle with parallel calls or complex argument schemas. For production-grade tool use, prefer 7B+ models.

**Finish-reason values across Ollama versions.** Some older Ollama versions return `"function_call"` instead of `"tool_calls"`. The labs check for both values where applicable.

**Round-trip count vs latency.** The sequential chain pattern makes more round-trips than parallel but each call is smaller. On local Ollama with no network latency, round-trip count matters less than on a cloud API where each call costs tokens and time.

---

## 9. Next Steps

After completing the three required labs and passing the criteria in `docs/structured-outputs/validation.md`:

→ Proceed to [`labs/rag/README.md`](../rag/README.md)

Note that RAG retrieval is typically implemented as a tool in agentic pipelines — the tool call cycle from `lab-tool-usage` directly underpins how RAG retrieval tools are wired in the `ai-agents` module.

If a lab produces unexpected output, consult the **Failure Modes** section of the corresponding topic document before modifying the lab code.
