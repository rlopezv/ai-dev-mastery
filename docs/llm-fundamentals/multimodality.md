---
id: "llm-fundamentals-multimodality"
title: "Multimodality"
type: "topic"
step: "llm-fundamentals"
path: "docs/llm-fundamentals/multimodality.md"
status: "final"
level: "foundational"
concepts:
  - "multimodality"
  - "vision-encoder"
  - "multimodal-model"
prerequisites:
  - "docs/llm-fundamentals/llm-architecture.md"
next:
  - "docs/llm-fundamentals/architecture.md"
related:
  - "docs/llm-fundamentals/tokenization.md"
  - "docs/llm-fundamentals/context-window.md"
implementation_refs: []
validation_refs:
  - "meta/standards/validation/docs-checklist.md"
summary: "Explains how multimodal models encode non-text inputs into the token embedding space and the engineering consequences for context budgeting, API usage, and system design."
---

# Multimodality

## Navigation

[Docs](../README.md) / [LLM Fundamentals](README.md) / Multimodality

---

## 1. Intuition

A transformer processes sequences of vectors. Text is converted to vectors through tokenization and embedding. Multimodality extends this by converting other input types — images, audio, video — into vectors in the same embedding space before the transformer sees them.

From the transformer's perspective, an image is just another sequence of vectors appended to the text embeddings. The attention mechanism does not distinguish between text-derived and image-derived vectors. The architecture stays the same; the preprocessing pipeline changes.

---

## 2. Explanation

### 2.1 Why

Text alone is insufficient for many practical tasks. Document analysis requires reading scanned pages. Customer support involves screenshots. Code review tools process architecture diagrams. Medical applications analyze imaging data alongside clinical notes.

Building separate models for each modality requires separate API calls, separate context windows, and loses the contextual relationship between modalities. A model that processes a screenshot and the associated error message together can reason about their relationship — something two separate models cannot do without an additional integration layer.

Multimodal models unify input processing: all modalities are encoded into a shared representation, processed by a single transformer, and generate a single coherent response. This reduces system complexity and enables cross-modal reasoning.

### 2.2 How

The core challenge is projecting non-text inputs into the same vector dimensionality as text embeddings so self-attention can operate uniformly across all of them.

**Image input — vision encoder**

The dominant approach uses a Vision Transformer (ViT) or convolutional encoder as a preprocessing stage:

1. The image is divided into fixed-size non-overlapping patches (typically 16×16 or 14×14 pixels).
2. Each patch is flattened and passed through the vision encoder, producing a dense vector per patch.
3. The patch vectors are linearly projected into the same embedding dimension as the language model's text token embeddings.
4. The projected patch vectors are concatenated with the text token embeddings and fed into the transformer's attention layers.

A 512×512 image with 16×16 patches produces 1,024 patch vectors — 1,024 additional "tokens" in the context window. Higher resolution produces more tokens proportionally.

**Audio input**

Audio is converted to a spectrogram — a frequency-time matrix representing sound energy across frequency bands over time. The spectrogram is encoded into patch-like vectors by an audio encoder (Whisper-style), then projected into the text embedding space using the same approach as images. One minute of audio produces roughly 1,500 encoded vectors.

**Video input**

Video is a sequence of image frames. Encoding every frame naively produces an enormous token sequence. Production systems use frame sampling — selecting representative frames at fixed or adaptive intervals — and temporal compression to reduce the token count while preserving temporal relationships. Video support is the most token-intensive and least widely available modality in current models.

**Unified attention**

Once all inputs are projected into the shared embedding space, the transformer's self-attention operates across all of them without modification. A text token can attend to an image patch vector and an image patch vector can attend to a text token — this is what enables cross-modal reasoning rather than parallel single-modality analysis.

### 2.3 Code example

```python
# No lab for this topic — concept-only
#
# Example: image + text prompt via the Ollama API with a vision-capable model
import requests
import base64

with open("architecture-diagram.png", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llava",
    "prompt": "Identify the components in this architecture diagram and describe how they connect.",
    "images": [image_b64],
    "stream": False,
})
print(response.json()["response"])
```

The image is base64-encoded and sent in the same API request as the text prompt. The model encodes the image patches internally and processes both alongside the text in a single forward pass.

---

## 3. Multimodal Input Characteristics

| Input type | Encoding approach | Approximate token cost | Key constraint |
|------------|-------------------|----------------------|----------------|
| Image — low resolution (512×512) | Vision encoder patches | 256–512 tokens | Minimum quality threshold |
| Image — high resolution (2048×2048) | Vision encoder patches | 1,500–4,000 tokens | Can dominate context budget |
| Audio — 1 minute | Spectrogram encoder | ~1,500 tokens | Scales with duration |
| Video — 10 seconds at 1 fps | Frame sampling + image encoder | ~2,500 tokens | Scales with frame count and resolution |
| PDF page rendered as image | Vision encoder patches | 500–1,500 tokens | Resolution-dependent |

---

## 4. Engineering Implications

**Images consume significant context tokens.** A single high-resolution image can consume 2,000–4,000 tokens — equivalent to several pages of dense text. Applications that process multiple images per request must budget for visual content explicitly. A prompt that fits comfortably in the context window without images may overflow when images are added.

**Resolution trades quality for cost.** Many providers offer image quality settings (low/high/auto) that control resolution before encoding. Lower resolution reduces token count and cost but can cause the model to miss fine details — small text in screenshots, precise labels in diagrams. The trade-off must be calibrated per use case; no single default works across all applications.

**Multimodal support is model-specific.** GPT-4o processes text, images, and audio. Claude processes text and images. Llava processes text and images. Video input is supported by a subset of frontier models only. API contracts differ between providers — image formats, maximum dimensions, and encoding strategies vary. Applications that switch providers must account for these differences.

**Multimodal output is not standard LLM behavior.** Current multimodal LLMs accept multi-modal input and produce text output. Image generation (DALL-E, Stable Diffusion, Midjourney) is a separate model class — diffusion models — not a feature of the transformer architectures covered here. Do not conflate multimodal input with multimodal output capability.

**Token counting for images is non-trivial.** Image token costs depend on resolution, tiling strategy, and model-specific encoding parameters. They cannot be computed by a standard text tokenizer. Always consult provider documentation for image-specific cost formulas before building billing estimates.

---

## 5. Implementation Connection

There is no lab for this topic. Vision-capable models (Llava) are available in the local Ollama setup used throughout this module, but multimodal labs are not part of the `llm-fundamentals` scope.

This topic provides the conceptual foundation for:

- The `llm-apis` module, which covers provider-specific multimodal API conventions for OpenAI, Anthropic, and Ollama
- The `rag` module, where PDFs and document images are sometimes processed as visual input rather than extracted text
- The `real-world-projects` module, where multimodal inputs appear in practical application scenarios

---

## 6. Failure Modes and Limitations

**Context overflow from images.** Adding images to a prompt that worked with text alone can silently push the total token count over the context window limit. Context truncation occurs without error, and the response degrades without an obvious cause. Always account for image token costs when estimating prompt size.

**Spatial reasoning is unreliable.** Multimodal models frequently make errors on tasks requiring precise spatial analysis: counting objects in dense images, reading tightly packed tables, identifying exact positions of elements. These limitations are well-documented in model evaluations and must be accounted for before relying on spatial reasoning in production.

**Hallucination applies to visual content.** Models can describe image content that is not present — inventing labels, misreading text, or confabulating details in ambiguous regions. Image descriptions should be treated as probabilistic claims, not authoritative readings, and validated the same way text outputs are.

**Resolution loss at low quality.** Low-quality image encoding to reduce token cost can cause the model to miss details that are critical to the task. A model that cannot read small text in a screenshot at low resolution is not failing due to a capability limitation — it is failing due to an infrastructure configuration decision. Quality settings must match the task's precision requirements.

---

## 7. Summary

Multimodal models extend the transformer's input space by encoding non-text inputs — images, audio, video — into the same vector embedding space as text, enabling unified self-attention across all modalities in a single forward pass. The primary engineering consequence is token cost: images add hundreds to thousands of tokens to the context window, directly affecting both pricing and available capacity. Multimodal support is model-specific, output remains primarily text, and spatial reasoning is an unreliable capability that requires explicit validation before production use.
