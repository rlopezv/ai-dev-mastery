---
id: "llm-fundamentals-tokenization"
title: "Tokenization"
type: "topic"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/tokenization.md"
status: "draft"
level: "foundational"
concepts:
  - "tokenization"
  - "byte-pair-encoding"
  - "token-vocabulary"
  - "tokenizer"
prerequisites:
  - "docs/llm-fundamentals/llm-architecture.md"
next:
  - "docs/llm-fundamentals/context-window.md"
related:
  - "docs/llm-fundamentals/inference-parameters.md"
implementation_refs:
  - "labs/llm-fundamentals/lab-tokenization"
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains how raw text is converted into token IDs, why token boundaries differ from word boundaries, and the engineering consequences for API cost, context budgeting, and cross-language behavior."
---

## 1. Intuition

A model does not read text. It reads integers. Tokenization is the translation layer between human-readable text and the integer sequences the model actually processes. The model has no concept of words, sentences, or characters — it operates exclusively on token IDs, each of which maps to a vector in the embedding space described in the previous topic.

Think of a tokenizer as a codec. Encoding converts a string into a sequence of integers. Decoding converts that sequence back into a string. The codec's rules — which byte sequences map to which IDs — are fixed at model training time and cannot be changed at runtime.

---

## 2. Explanation

### 2.1 Why

Early language models used character-level or word-level tokenization. Character-level models required very long sequences to represent normal text, making attention computation expensive. Word-level models required fixed vocabularies that broke on rare words, inflected forms, and out-of-vocabulary terms.

Byte Pair Encoding (BPE), the algorithm underlying tokenizers in GPT, Llama, and most modern LLMs, solves both problems. It builds a vocabulary of subword units by iteratively merging the most frequent adjacent pairs in a training corpus. Common words become single tokens; rare words decompose into known subword fragments. Any input — including code, URLs, and arbitrary Unicode — can be represented without an "unknown" token. The vocabulary size (typically 32k–100k entries) is a deliberate trade-off between representation efficiency and the size of the embedding matrix the model must learn.

### 2.2 How

Tokenization operates differently at training time and inference time.

**Vocabulary construction (training time)**
The tokenizer is trained on a large text corpus independently of the language model. Starting from a base of 256 byte values, it repeatedly identifies the most frequent adjacent pair across the corpus and merges them into a new vocabulary entry. This continues until the vocabulary reaches its target size. The resulting merge rules are saved alongside the vocabulary and shipped with the model.

**Encoding (inference time)**
Given an input string, the tokenizer applies two stages:
1. A regex splits the text into pre-tokens — roughly word-sized chunks including surrounding whitespace and punctuation. This prevents merges from crossing word boundaries in ways that would produce unstable encodings.
2. Each pre-token is encoded by applying the saved BPE merge rules in order, converting the byte sequence into the longest token IDs available in the vocabulary.

The output is a flat list of integers. The transformer receives this list directly.

**Decoding**
Each token ID maps back to a byte sequence. Concatenating these sequences and decoding as UTF-8 reconstructs the original string. Decoding is deterministic and lossless.

One consequence: **token boundaries are determined by corpus statistics, not by linguistic structure.** The word "tokenization" might be a single token or split into ["token", "ization"] — depending on how frequently it appeared in the training data. Spacing matters too: " Paris" (with a leading space) and "Paris" are typically different token IDs.

### 2.3 Code example

```python
# See: labs/llm-fundamentals/lab-tokenization/main.py
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

text = "The transformer architecture uses self-attention."
tokens = enc.encode(text)

print(tokens)          # list of integer token IDs
print(len(tokens))     # 8 tokens for 7 words
print(enc.decode(tokens))  # reconstructs original string exactly
```

---

## 3. Tokenization Behavior by Input Type

| Input | Approx. tokens (cl100k_base) | Notes |
|-------|------------------------------|-------|
| `"Hello world"` | 2 | Common English — near word-level |
| `"Hola mundo"` | 3 | Spanish — less training data frequency |
| `"transformer"` | 1 | High-frequency technical term |
| `"antidisestablishmentarianism"` | 6 | Rare word decomposes into subwords |
| `"print('hello')"` | 6 | Code tokenizes with reasonable efficiency |
| `"こんにちは"` | 5 | Japanese — each character is approximately one token |
| `" Paris"` | 1 | Leading space included in the token |
| `"Paris"` | 1 | Same word, different token ID from `" Paris"` |
| `"2024-04-15"` | 4 | Dates and numbers tokenize character by character |

---

## 4. Engineering Implications

**API cost is per token.** All major LLM APIs charge per input token and per output token. Character count and word count are not proxies for cost. A 1,000-word English document is roughly 1,300 tokens; the same content in Japanese may be 2,500 tokens. Accurate cost estimation requires tokenizing the actual prompt before sending it.

**Context window is measured in tokens.** You cannot determine from a document's character or word count whether it fits in the context window. Always tokenize explicitly when the budget matters. A document that "should fit" in 8k tokens may exceed it once formatted as a prompt with system instructions and conversation history.

**Different models use different tokenizers.** GPT-4, Claude, and Llama3 each ship with their own tokenizer trained on their own corpus. The same text produces different token counts and different token IDs across models. Token-count assumptions from one model do not transfer to another.

**Non-Latin text is more expensive.** Languages with large character sets or lower representation in LLM training corpora produce more tokens per unit of information than English. This directly reduces effective context capacity for multilingual applications.

**Spacing and capitalization change token IDs.** Prompt construction by string concatenation can produce unexpected token splits at join boundaries. A word that is one token in isolation may split into two when preceded by a newline or another word without a space.

---

## 5. Implementation Connection

`labs/llm-fundamentals/lab-tokenization` uses the `tiktoken` library to make tokenization directly observable. The lab demonstrates:

- Encoding text and inspecting the raw integer token IDs
- Counting tokens for different input types: short English, long English, non-English, code, and numbers
- Observing that the same semantic content produces different token sequences in different tokenizers
- Computing the token cost of a prompt before sending it to an API

The lab requires no running model — the tokenizer operates as a standalone library. This isolates tokenization from generation, making the behavior easy to test and introspect.

---

## 6. Failure Modes and Limitations

**Token budget underestimation.** Estimating context window usage from word or character count is unreliable. Non-English content, code, structured data (JSON, XML), and numbers all tokenize with different efficiency than prose English. The only accurate method is to run the tokenizer before sending the request.

**Tokenizer version mismatch.** Using the wrong tokenizer for a model produces incorrect token counts. `cl100k_base` (GPT-4) and `o200k_base` (GPT-4o) are distinct tokenizers; the difference is small but significant for tight budget calculations and billing estimates.

**Mid-word token splits.** When a key term in a prompt splits across multiple tokens, the model's attention over it is distributed differently than when it is a single token. This is rarely a practical issue in normal usage but is relevant in adversarial contexts and in fine-tuning dataset preparation.

**Single character changes cascade.** BPE is not locally stable: changing or inserting one character can shift all token boundaries in a pre-token, producing a completely different token sequence. This matters for prompt injection research and for any system that modifies prompts after tokenization.

---

## 7. Summary

Tokenization converts text to a flat list of integer token IDs using a subword vocabulary built by Byte Pair Encoding. Token boundaries are statistically determined, not linguistically motivated, and they differ across models. The practical consequences are concrete: API cost is proportional to token count, context window capacity is consumed in tokens, and non-English content is more expensive per unit of information. Always tokenize explicitly when budget or fit matters — never estimate from character or word count.
