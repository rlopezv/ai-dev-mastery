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

## Overview

This lab uses `tiktoken` as a standalone tool — no Ollama required. It makes tokenization behavior directly observable: how text becomes integers, why different input types produce different token counts, and why leading spaces and single-character changes matter.

**Out of scope:** model-specific tokenizers (Llama SentencePiece), tokenization during live inference.

---

## Concepts

| Concept | Where it appears |
|---------|-----------------|
| `tokenization` | `observe_round_trip()` — encode produces integer IDs; decode reconstructs the original string losslessly |
| `byte-pair-encoding` | `observe_character_sensitivity()` — one character change shifts BPE merge rules, producing a different ID sequence |
| `token-vocabulary` | `observe_leading_space()` — `'Paris'` and `' Paris'` map to different vocabulary IDs |

---

## Setup

```bash
# No server required. Install dependencies only:
pip install -r labs/llm-fundamentals/requirements.txt
```

---

## Run

```bash
cd labs/llm-fundamentals
python lab-tokenization/main.py
```

---

## Expected Output

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

=== Observation 5: Token budget estimate ===
  System prompt:   18 tokens
  User message:    12 tokens
  Max output:     256 tokens
  Grand total:    286 tokens
  Fits in 2048:   yes
  Fits in 512:    yes
  Fits in 256:    no
```

---

## What to observe

- **Observation 2:** Non-English content costs more tokens than equivalent English. Spanish produces ~10–15% more tokens; Japanese 2–4× more. Both directly affect API cost and context window capacity in multilingual applications.
- **Observation 3:** `'Paris'` and `' Paris'` have different token IDs. String concatenation without careful spacing produces unexpected tokenization at join boundaries.
- **Observation 4:** Changing one character changes which BPE merges apply, sometimes producing a different token sequence for the rest of the word.
- **Observation 5:** The budget estimate shows that `grand_total` can exceed common context limits (256, 512) even for short-seeming prompts once output reservation is included.

---

## Concepts verified

- [ ] Token IDs differ for a word with and without a leading space — observable at Observation 3
- [ ] Non-Latin text costs more tokens than equivalent English — observable at Observation 2
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

## Infrastructure

| Service | Purpose |
|---------|---------|
| tiktoken | Standalone tokenizer library — runs in-process, no server required |
