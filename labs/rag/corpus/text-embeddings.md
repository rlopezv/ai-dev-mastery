# Text Embeddings

Search engines traditionally work by matching words. You search for "transformer architecture" and the engine finds documents that contain those exact words. This works until the document you need talks about "attention mechanisms" or "self-attention layers" without ever using the phrase you typed. Embeddings fix this by moving from word matching to meaning matching.

## What an Embedding Is

An embedding model is a neural network trained to map text to a point in high-dimensional space — a vector of typically 768 or 1536 floating-point numbers. The key property is geometric: texts that mean similar things end up close together, regardless of the words they use. "How does attention work?" and "Explain the self-attention mechanism" produce vectors that are close in this space, even though they share almost no words.

The embedding is produced by passing the text through the model and pooling the token representations into a single fixed-size vector. The two most common pooling strategies are **mean pooling** — averaging all token vectors — and using the representation of a special [CLS] token placed at the beginning of the input. Most modern sentence embedding models use mean pooling, which tends to produce more stable representations for variable-length inputs.

## Measuring Similarity: Cosine Similarity

The standard way to compare two embedding vectors is **cosine similarity**, defined as:

```
cosine_similarity(a, b) = (a · b) / (|a| × |b|)
```

It measures the cosine of the angle between the two vectors. The result ranges from -1 (pointing in opposite directions) to 1 (pointing in the same direction) and is scale-invariant — it ignores vector magnitude, so document length doesn't distort the score. In practice, a score above 0.75 indicates strong semantic overlap; below 0.5 usually means the texts are unrelated for retrieval purposes. Scores between 0.5 and 0.75 are a grey zone where adjacent or partially relevant content tends to sit.

## Embedding Models Available Locally

Ollama serves several embedding models without requiring a cloud API:

- **nomic-embed-text** — 768 dimensions, fast inference, strong benchmark performance. Supports up to 8192 tokens. A practical default for most RAG applications.
- **mxbai-embed-large** — 1024 dimensions, higher retrieval quality on MTEB benchmarks, noticeably slower. Worth the cost when precision matters.
- **all-minilm-l6-v2** — 384 dimensions, very fast. Appropriate when throughput is the priority and some quality loss is acceptable.

All three are accessed through the same OpenAI-compatible `/v1/embeddings` endpoint.

## Practical Constraints

**Consistency is non-negotiable.** Every vector in an index must come from the same model and the same model version. A vector from `nomic-embed-text` and one from `mxbai-embed-large` live in incompatible spaces — comparing them produces meaningless scores. Changing the embedding model means deleting the index and rebuilding it from scratch.

**Batch requests save time.** The embedding API accepts arrays of texts. Sending 64 texts in one request instead of 64 separate requests reduces total time by an order of magnitude — at small input sizes, the network round-trip overhead dominates the actual compute cost.

**Domain gaps are real.** A model trained on general web text may not capture the semantic structure of specialised domains like medical imaging, contract law, or proprietary codebases. For narrow domains, fine-tuned embedding models typically outperform general-purpose ones on retrieval benchmarks.
