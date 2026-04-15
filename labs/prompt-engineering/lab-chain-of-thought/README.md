# lab-chain-of-thought

**Module:** `prompt-engineering`
**Type:** implementation
**Doc:** `docs/prompt-engineering/chain-of-thought.md`
**Required:** yes

## What this lab demonstrates

- Direct answer vs chain-of-thought accuracy on multi-step word problems
- Answer extraction using the `"Answer:"` marker
- Visible reasoning trace and where it helps vs where it is unnecessary

## Prerequisites

- Ollama running: `ollama serve` + `ollama pull llama3.2`
- `pip install -r labs/prompt-engineering/requirements.txt`

## Run

```bash
cd labs/prompt-engineering
python lab-chain-of-thought/main.py
```

## Expected output

```
=== Chain-of-Thought vs Direct Answering ===

--- Problem 1 ---
  Problem: A warehouse has 240 boxes...
  Direct  → '105'  (normalized: 105)  ✓
  CoT     → extracted: '105'  (normalized: 105)  ✓
  Expected: 105

--- Problem 2 ---
  Problem: Alice is twice as old as Bob...
  Direct  → '13'  (normalized: 13)  ✗
  CoT     → extracted: '26'  (normalized: 26)  ✓
  Expected: 26

Results:  Direct 1/3   CoT 3/3
```

## Concepts verified

- CoT correct count ≥ direct correct count on multi-step problems
- `"Answer:"` marker present in every CoT response
- `parse_cot_answer` returns clean numeric answer without reasoning trace
