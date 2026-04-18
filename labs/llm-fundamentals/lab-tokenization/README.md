---
id: "lab-tokenization"
title: "Tokenization"
type: "lab-readme"
step: "llm-fundamentals"
path: "labs/llm-fundamentals/lab-tokenization/README.md"
status: "draft"
level: "foundational"
concepts:
  - "tokenization"
  - "byte-pair-encoding"
  - "token-vocabulary"
prerequisites:
  - "docs/llm-fundamentals/tokenization.md"
related:
  - "docs/llm-fundamentals/README.md"
summary: "Observation lab — makes tokenization behavior directly measurable: encode/decode round-trips, token count variance by language and input type, and leading-space sensitivity."
---

# Tokenization
## Navigation

[Labs](../../README.md) / [LLM Fundamentals — Labs](../README.md) / Tokenization

---

**Module:** llm-fundamentals  
**Type:** observation  
**Doc:** `docs/llm-fundamentals/tokenization.md`

---

## What this lab demonstrates

This lab uses `tiktoken` (the OpenAI tokenizer library) as a standalone tool — no Ollama required. It makes tokenization behavior directly observable: how text becomes integers, why different input types produce different token counts, and why leading spaces and single-character changes matter.

**Observations:**
1. Encode/decode round-trip — tokenization is lossless
2. Token count varies significantly by input type and language
3. Leading space changes the token ID for the same word
4. One character change can cascade through the entire token sequence
5. Token budget estimation for a realistic prompt

---

## How to run

```bash
# From the labs/llm-fundamentals/ directory:
python lab-tokenization/main.py
```

**Prerequisites:** `tiktoken` installed (`pip install tiktoken`). No Ollama needed.

---

## Expected output

```
Tokenizer: cl100k_base

=== Observation 1: Round-trip encode → decode ===
Input:   'The quick brown fox jumps over the lazy dog.'
IDs:     [791, 4062, 8516, ...]
Count:   9 tokens
Decoded: 'The quick brown fox jumps over the lazy dog.'
✓ Round-trip is lossless

=== Observation 2: Token count by input type ===
  English — common words               →   9 tokens  'The transformer architecture...'
  English — rare word                  →   6 tokens  'antidisestablishmentarianism'
  Spanish                              →  10 tokens  'La arquitectura transformer...'
  Japanese                             →  22 tokens  'トランスフォーマーアーキテクチャは...'
  Python code                          →  12 tokens  'def encode(text: str)...'
  Numbers / date                       →   7 tokens  '2024-04-15 at 09:30:00'
  ...

=== Observation 3: Leading space changes token ID ===
  'Paris'  → [60704]
  ' Paris' → [12366]
  ...

=== Observation 4: Character sensitivity ===
  'tokenization'  → [47058, 2065] (2 tokens)
  'tokenizations' → [47058, 4024] (2 tokens, different second token)
  ...
```

---

## What to observe

- **Observation 2:** Japanese uses 2–4× more tokens than equivalent English content. This directly affects API cost and context window capacity for multilingual applications.
- **Observation 3:** `'Paris'` and `' Paris'` have different token IDs. String concatenation without careful spacing can produce unexpected tokenization.
- **Observation 4:** Changing one character changes which BPE merges apply, sometimes producing a completely different token sequence for the rest of the word.
- **Observation 5:** The budget estimate shows that `grand_total` can exceed common context limits (2048, 4096) even for short-seeming prompts.

---

## Concepts verified

- [ ] Token IDs differ for a word with and without a leading space — observable at Observation 3
- [ ] Non-Latin text costs 2–4× more tokens than equivalent English — observable at Observation 2
- [ ] A single character change can alter the full token sequence for a word — observable at Observation 4
- [ ] Token count, not character count, determines API cost and context fit — observable at Observation 5

---

## Failure case

Modify `main.py` at the `# FAILURE CASE` block and re-run.

- **What to change:** in `observe_budget_estimate()`, set `max_output = 0`
- **Expected degradation:**
  - All three context limits report `fits: yes` even for prompts that would overflow at runtime
  - Simulates the common mistake of computing only input tokens and forgetting to reserve space for the model's response

Restore `max_output = 256` after the experiment.

---

## Configuration

No environment variables needed. The tokenizer runs entirely in-process.
