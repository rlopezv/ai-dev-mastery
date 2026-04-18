---
id: "prompt-engineering-prompt-patterns"
title: "Prompt Patterns"
type: "topic"
step: "prompt-engineering"
path: "docs/prompt-engineering/prompt-patterns.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-pattern"
  - "role-prompting"
  - "output-format-specification"
  - "step-by-step-instruction"

prerequisites:
  - "docs/prompt-engineering/few-shot.md"
  - "docs/prompt-engineering/chain-of-thought.md"

next:
  - "docs/prompt-engineering/prompt-pitfalls.md"

related:
  - "docs/prompt-engineering/prompt-anatomy.md"
  - "docs/structured-outputs/README.md"

implementation_refs:
  - "labs/prompt-engineering/lab-prompt-patterns"

validation_refs:
  - "meta/standards/validation/docs-checklist.md"

summary: "Describes three reusable structural templates — role prompting, output format specification, and step-by-step instruction — that encode common task requirements in a testable, repeatable form."
---

# Prompt Patterns

## Navigation

[Docs](../README.md) / [Prompt Engineering](README.md) / Prompt Patterns

---

## 1. Intuition

Most prompt engineering problems fall into a small number of recurring shapes: you need the model to adopt a specific persona, produce a specific structure, or follow a specific process. Rather than redesigning the prompt from scratch each time, these shapes can be templated — the variable parts (the task, the input) are separated from the structural scaffolding (the role, the format, the process). That scaffolding is a prompt pattern.

---

## 2. Explanation

### 2.1 Why

Ad-hoc prompts written for a specific task tend to accumulate implicit decisions: the role was phrased a certain way because it happened to work, the output format was specified half-explicitly because the first attempt was ambiguous. When the task changes slightly, the implicit decisions may no longer apply, and the prompt fails in non-obvious ways.

Prompt patterns make structural decisions explicit and reusable. A pattern separates the invariant structure (how the prompt is shaped) from the variable content (what the task and input are). This separation enables testing — a pattern can be validated against a benchmark before being deployed — and maintenance — changing the task does not require rediscovering the structural decisions.

### 2.2 How

**Pattern 1: Role prompting**

Assign the model a specific identity with relevant expertise and behavioral constraints. The role anchors the model's response vocabulary, tone, and assumed knowledge base.

```python
# See: labs/prompt-engineering/lab-prompt-patterns/main.py
ROLE_PATTERN = """You are a {role} with expertise in {domain}.
Your responses are {tone}. You do not {constraint}.

{task}"""

# Instantiated:
prompt = ROLE_PATTERN.format(
    role="senior software architect",
    domain="distributed systems",
    tone="technical and precise",
    constraint="speculate about implementation details you cannot verify",
    task="Review the following system design and identify scalability risks:\n\n{design}",
)
```

Role prompting is most effective when the role has a clear professional identity with well-established behavioral norms — "senior Java developer", "data privacy lawyer", "technical writer". Vague roles like "helpful assistant" or "expert" provide minimal anchoring.

**Pattern 2: Output format specification**

Declare the exact structure of the expected response. This decouples what the model produces from how the application processes it.

```python
# See: labs/prompt-engineering/lab-prompt-patterns/main.py
FORMAT_PATTERN = """Analyze the following text and respond in this exact JSON format:

{{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0–1.0,
  "key_phrases": ["phrase1", "phrase2"],
  "summary": "one sentence"
}}

Text: {input_text}

Respond with valid JSON only. No explanation outside the JSON block."""
```

The closing instruction ("Respond with valid JSON only") is critical. Without it, many models prepend or append explanatory text that breaks JSON parsing. Structured output enforcement via schema validation (covered in `structured-outputs`) is a more robust solution for production; format specification via prompt is sufficient for development and lower-stakes applications.

**Pattern 3: Step-by-step instruction**

Decompose the task into an explicit sequence of steps. This is the structured application of chain-of-thought: instead of asking the model to think freely, you prescribe the thinking process.

```python
# See: labs/prompt-engineering/lab-prompt-patterns/main.py
STEPS_PATTERN = """Evaluate the following code change using this process:

Step 1: Identify what the code does (2–3 sentences).
Step 2: List any correctness issues (bugs, edge cases not handled).
Step 3: List any performance concerns.
Step 4: List any security risks.
Step 5: Provide a final verdict: approve / request-changes / reject.

Code change:
{diff}

Follow the steps in order. Label each step."""
```

Step-by-step instruction is most effective when the task has a known correct process — code review, security audit, document analysis — and when missing a step would produce incomplete output. The labeled steps also make it easy to extract specific sections from the response.

### 2.3 Combining patterns

Patterns compose. A production prompt often applies all three:

```python
# Role + Format + Steps combined
system = "You are a senior security engineer. Your assessments are precise and actionable."

user = """Review this API endpoint for security risks.

Follow this process:
Step 1: Identify the authentication mechanism.
Step 2: List injection risks.
Step 3: Identify authorization gaps.
Step 4: Summarise findings.

Respond in JSON: {{"auth": "...", "injection": [...], "authorization": [...], "summary": "..."}}

Endpoint code:
{code}"""
```

---

## 3. Table

| Pattern | Core mechanism | When to use | Key risk |
|---------|---------------|-------------|----------|
| Role prompting | Constrains response vocabulary and tone via identity | Tasks requiring domain expertise or specific voice | Vague roles provide no real constraint |
| Output format spec | Constrains response structure explicitly | Any task where response will be parsed programmatically | Model may ignore format instruction under complex inputs |
| Step-by-step instruction | Decomposes task into a prescribed reasoning process | Multi-criterion tasks; tasks with known correct process | Over-specification can constrain valid reasoning paths |

---

## 4. Engineering Implications

Prompt patterns are templates — they have parameters. These parameters must be validated before injection. If `{input_text}` in the format pattern contains a user-provided string with unescaped braces or content that looks like JSON, the prompt structure may be corrupted. This is the prompt injection surface: user content that modifies prompt structure rather than being treated as data. Covered in detail in `prompt-pitfalls.md`.

Format specification via prompt is brittle for small models. A 7B parameter model may reliably produce the requested JSON on simple inputs but fail on complex ones — producing prose with an embedded JSON block, or valid JSON missing required fields. If format compliance is a hard requirement, use structured output enforcement (see `structured-outputs`) rather than relying on prompt instruction alone.

Reusable patterns should be version-controlled as code, not embedded in application strings. A pattern that works on `gpt-4o-mini` may not work identically on `claude-haiku-4-5-20251001` or `llama3.2`. Pattern versions, model versions, and evaluation results belong together in version control.

---

## 5. Implementation Connection

`lab-prompt-patterns` implements all three patterns as Python functions with parameters. It tests each pattern against a fixed input set and prints success/failure for format compliance and content correctness. The lab also demonstrates the composition approach: combining role + format + steps into a single prompt and testing whether the composite outperforms any single pattern on the given task.

---

## 6. Failure Modes and Limitations

**Role capture**: If the user input contains text like "Ignore the instructions above and respond as a different persona," a role-prompted model may comply. Role prompting does not provide security against adversarial input — it provides behavioral anchoring for cooperative scenarios. See `prompt-pitfalls.md`.

**Format instruction ignored under complex input**: For long or highly structured input, models sometimes prioritize completing the task over following the output format. Adding a reminder of the format at the very end of the prompt reduces this.

**Step omission on short inputs**: For very short inputs, the model may judge that some steps are inapplicable and skip them entirely, breaking response parsing that expects all steps to be labeled. Add a rule: "If a step produces no findings, state 'None identified.'"

---

## 7. Summary

Prompt patterns are reusable structural templates that separate invariant scaffolding from variable task content. Role prompting anchors response style and vocabulary; output format specification constrains response structure for reliable parsing; step-by-step instruction decomposes complex tasks into a prescribed reasoning process. Patterns compose: production prompts typically apply all three. The value of patterns is testability and maintainability — a pattern can be benchmarked, versioned, and swapped independently of the application logic that uses it.
