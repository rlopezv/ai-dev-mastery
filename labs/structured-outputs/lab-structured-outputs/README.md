# lab-structured-outputs

**Module:** `structured-outputs`
**Type:** implementation
**Doc:** `docs/structured-outputs/structured-outputs.md`
**Required:** yes

## What this lab demonstrates

- Observation 1: prompt-only JSON format instruction — shows parse failures on adversarial inputs
- Observation 2: JSON mode enabled — syntactic validity guaranteed, shape still model-determined
- Observation 3: Pydantic schema enforcement — `message.parsed` returns a typed `ReviewSummary` object with zero parse failures

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/structured-outputs/requirements.txt`

## Run

```bash
cd labs/structured-outputs
python lab-structured-outputs/main.py
```

## Expected output

```
=== Observation 1: Prompt-only JSON ===
Input 1: "Great product, fast delivery!"
  raw: {"sentiment": "positive", "score": 5, "key_issues": []}
  parsed: OK
Input 2: "The item was okay but shipping took forever and packaging was damaged."
  raw: I'd classify this review as neutral...{"sentiment": "neutral"...}
  parsed: FAIL — extra prose before JSON
...
Prompt-only parse success: 3/5

=== Observation 2: JSON mode ===
Input 1: {"sentiment": "positive", "score": 5, "key_issues": []}
  valid JSON: yes | conforms to schema: unknown (no enforcement)
...
JSON mode parse success: 5/5 | Schema compliance: manual check required

=== Observation 3: Schema enforcement (Pydantic) ===
Input 1: ReviewSummary(sentiment='positive', score=5, key_issues=[])
Input 2: ReviewSummary(sentiment='neutral', score=3, key_issues=['slow shipping', 'damaged packaging'])
...
Schema enforcement parse success: 5/5
All typed objects. No manual json.loads needed.
```

## Concepts verified

- Prompt-only JSON fails on adversarial inputs (long text, special characters)
- JSON mode guarantees syntactic validity but not structural conformance
- Pydantic schema enforcement returns a typed object from `message.parsed` with zero failures
- `sentiment` is always one of `["positive", "neutral", "negative"]`; `score` is always 1–5
