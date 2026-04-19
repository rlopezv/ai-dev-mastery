---
id: "prompt-engineering-labs-readme"
title: "Prompt Engineering — Labs"
type: "lab-readme"
step: "prompt-engineering"
path: "labs/prompt-engineering/README.md"
status: "draft"
level: "foundational"

concepts:
  - "prompt-anatomy"
  - "few-shot-prompting"
  - "chain-of-thought"
  - "prompt-pattern"
  - "output-format-specification"

prerequisites:
  - "docs/prompt-engineering/implementation-reference.md"

next:
  - "labs/structured-outputs/README.md"

related:
  - "docs/prompt-engineering/README.md"

implementation_refs:
  - "labs/prompt-engineering/lab-prompt-anatomy"
  - "labs/prompt-engineering/lab-few-shot"
  - "labs/prompt-engineering/lab-chain-of-thought"
  - "labs/prompt-engineering/lab-prompt-patterns"

validation_refs:
  - "meta/standards/validation/labs-checklist.md"

summary: "Four labs that make prompt engineering techniques directly observable — anatomy component effects, few-shot accuracy improvement, chain-of-thought reasoning, and reusable pattern templates with a benchmark harness."
---

# Prompt Engineering — Labs

## Navigation

[Labs](../README.md) / Prompt Engineering — Labs

---


## 1. Overview

These labs implement and measure the prompt engineering techniques described in `docs/prompt-engineering/`. Each lab isolates one technique, runs it against a fixed input set, and produces measurable output that confirms the concept.

All labs run against Ollama locally. No cloud API keys are required. Results vary by model — the techniques are observable on any capable open-weight model; absolute accuracy numbers depend on model size.

**Not covered:**
- Structured output schema enforcement (see `structured-outputs`)
- RAG context injection (see `rag`)
- Prompt pitfalls (concept-only, no lab)

---

## 2. Lab Inventory

| Lab | Demonstrates | Type | Required | Doc |
|-----|-------------|------|----------|-----|
| `lab-prompt-anatomy` | Effect of removing each prompt component on output consistency | observation | yes | `prompt-anatomy.md` |
| `lab-few-shot` | Accuracy improvement from zero-shot to three-shot classification | implementation | yes | `few-shot.md` |
| `lab-chain-of-thought` | Direct vs CoT accuracy on multi-step reasoning; answer extraction | implementation | yes | `chain-of-thought.md` |
| `lab-prompt-patterns` | Role, format, and step-by-step patterns with benchmark harness | implementation | yes | `prompt-patterns.md` |

---

## 3. Execution Model

All labs use the **`foundational` infrastructure profile**: Ollama running locally via the OpenAI-compatible interface.

**Prerequisites:**

```bash
# 1. Start Ollama
ollama serve
ollama pull llama3.2

# 2. Install dependencies
pip install -r labs/prompt-engineering/requirements.txt

# 3. Configure environment
cd labs/prompt-engineering
cp .env.example .env
# Edit .env if Ollama runs on a non-default URL or you want a different model
```

**Running a lab:**

```bash
cd labs/prompt-engineering
python lab-prompt-anatomy/main.py
python lab-few-shot/main.py
python lab-chain-of-thought/main.py
python lab-prompt-patterns/main.py
```

Each lab prints structured output to stdout. No server process is started.

---

## 4. Lab Structure

```text
labs/prompt-engineering/
├── README.md                        ← this file
├── .env.example                     ← environment variable template
├── requirements.txt                 ← Python dependencies
├── shared/
│   ├── __init__.py
│   └── config.py                    ← environment variable loader + API client
├── lab-prompt-anatomy/
│   ├── README.md
│   └── main.py
├── lab-few-shot/
│   ├── README.md
│   └── main.py
├── lab-chain-of-thought/
│   ├── README.md
│   └── main.py
└── lab-prompt-patterns/
    ├── README.md
    └── main.py
```

Each lab is self-contained. The only cross-lab dependency is `shared/config.py`.

---

## 5. Mapping to Documentation

| Documentation | Lab |
|---------------|-----|
| `docs/prompt-engineering/prompt-anatomy.md` | `lab-prompt-anatomy` |
| `docs/prompt-engineering/few-shot.md` | `lab-few-shot` |
| `docs/prompt-engineering/chain-of-thought.md` | `lab-chain-of-thought` |
| `docs/prompt-engineering/prompt-patterns.md` | `lab-prompt-patterns` |
| `docs/prompt-engineering/prompt-pitfalls.md` | — (concept-only) |

---

## 6. Validation

**lab-prompt-anatomy**
```
Expected: complete prompt produces consistent output across 5 runs;
          removing output format spec produces format variation;
          removing instruction produces off-task responses.
```

**lab-few-shot**
```
Expected: 3-shot accuracy ≥ zero-shot accuracy on the test set;
          output format is consistent when examples enforce it;
          accuracy printed as correct/total for each shot count.
```

**lab-chain-of-thought**
```
Expected: at least one problem where direct answer is wrong and CoT is correct;
          "Answer:" marker is present in every CoT response;
          parse_cot_answer returns clean final answer without reasoning trace.
```

**lab-prompt-patterns**
```
Expected: role pattern produces domain-appropriate vocabulary;
          format pattern produces valid JSON on all test inputs;
          steps pattern labels all required sections;
          benchmark harness prints accuracy ≥ 70% for each pattern.
```

---

## 7. Common Issues

**Ollama not reachable.**
Each lab checks connectivity at startup. Start Ollama with `ollama serve` and retry.

**Model not found.**
Default is `llama3.2`. Run `ollama pull llama3.2` or set `OLLAMA_MODEL` in `.env`.

**JSON parsing fails in lab-prompt-patterns.**
Small models (3B) sometimes produce prose before or after the JSON block. The lab includes a lenient JSON extractor that strips surrounding text. If it still fails, try a larger model: set `OLLAMA_MODEL=llama3.2:latest` or a 7B variant.

**CoT answer not extracted.**
If the model does not produce the "Answer:" marker, the parser raises `ValueError`. The lab prints the full response for inspection. Try rephrasing the extraction instruction or increase `MAX_TOKENS`.

**Accuracy below expected.**
Results depend heavily on model size. A 3B model will score lower than a 7B model on classification tasks. The labs measure relative improvement (0-shot vs 3-shot), not absolute scores — the technique is validated even if absolute accuracy is modest.

---

## 8. Engineering Notes

**Determinism vs. variation.** Labs that run the same prompt multiple times to measure consistency use `temperature=0` to minimize randomness. Labs that measure accuracy across different inputs use `temperature=0.1` — low but not zero — to avoid degenerate repetition on consecutive calls.

**Token budget.** Few-shot examples in `lab-few-shot` add approximately 150 tokens per run. For a 10-item test set at 3 shots, total extra prompt cost is ~1,500 tokens. On a free local model this is irrelevant; on a cloud API it is a cost consideration.

**Benchmark accuracy interpretation.** A 70% accuracy on an 8-item test set means 5–6 correct. These numbers are illustrative, not production benchmarks. The purpose is to make the accuracy delta between techniques observable, not to establish absolute performance figures.

---

## 9. Next Steps

After completing all four labs and passing the criteria in `docs/prompt-engineering/validation.md`:

→ Proceed to [`labs/structured-outputs/README.md`](../structured-outputs/README.md)

If a lab produces unexpected output, consult the **Failure Modes** section of the corresponding topic document before modifying the lab code.
