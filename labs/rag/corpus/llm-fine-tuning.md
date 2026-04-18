# LLM Fine-Tuning

A pre-trained language model knows a great deal — it has absorbed patterns from hundreds of billions of words of text. But it does not know your domain, your style, or your company's internal vocabulary. Fine-tuning is the process of continuing a model's training on a specific dataset to shift its behaviour toward what you need. It modifies the model's weights, so the adaptation persists at inference time without any changes to the prompt.

## When Fine-Tuning Makes Sense

Fine-tuning is most valuable when you need **consistent behaviour** that is difficult to achieve reliably through prompting alone:

**Format and style consistency** — if your application always needs output in a specific structure (a particular JSON schema, a formal report in a house style), fine-tuning on examples of correct outputs makes that structure automatic rather than prompted.

**Domain vocabulary** — terms that are rare in general web text (ICD medical codes, proprietary API method names, contract law phrases) may have weak embeddings and unreliable model behaviour. Fine-tuning on domain examples improves the model's fluency with those terms.

**Task specialisation at scale** — for high-volume use cases, including few-shot examples in every prompt is expensive in tokens. A fine-tuned model absorbs the task pattern into its weights and can be called with a shorter, cheaper prompt.

## What Fine-Tuning Is Not Good For

Fine-tuning is a poor tool for updating factual knowledge. New facts added through fine-tuning are retrieved less reliably than facts from the original training data, and the model may confabulate when fine-tuning data conflicts with pre-training patterns. For knowledge that changes over time or is domain-specific, Retrieval-Augmented Generation is a more reliable approach — the knowledge lives in a document store that can be updated without touching the model.

| Dimension | Fine-tuning | RAG |
|-----------|-------------|-----|
| Knowledge freshness | Requires retraining to update | Update the document store |
| Answer traceability | None | Full (source chunks) |
| Setup cost | High (GPU, data curation, training time) | Moderate (index build) |
| Best suited for | Style, format, task specialisation | Dynamic or private knowledge |

## Supervised Fine-Tuning

The most common method is **supervised fine-tuning (SFT)**: train the model on labelled (input, output) pairs using the same next-token prediction loss used in pre-training. A small learning rate — typically 1e-5 to 5e-5 — prevents the new examples from overwriting the general capabilities the model already has. Training runs for one to five epochs on a curated dataset. Data quality matters more than quantity: 1,000 high-quality, diverse examples typically outperforms 100,000 noisy or redundant ones.

## LoRA: Efficient Adaptation

Updating all the weights of a 7-billion-parameter model requires significant GPU memory and time. **LoRA (Low-Rank Adaptation)** reduces this by inserting small trainable adapter matrices alongside the frozen original weight matrices in the attention layers. If the original weight matrix W has shape (d × d), LoRA replaces its update with two smaller matrices A (d × r) and B (r × d) where rank r ≪ d — typically 8 to 64. Only A and B are trained, reducing trainable parameters by 10 to 100 times while maintaining performance close to full fine-tuning.

LoRA adapters are compact (typically 20–200 MB) and can be swapped at inference time without reloading the base model, making it practical to maintain multiple specialised variants of the same base model.

## Catastrophic Forgetting

Heavy fine-tuning on a narrow domain can degrade the model's performance on tasks outside that domain — the new weight updates overwrite patterns needed for general reasoning. Mitigation strategies include mixing a small proportion of general-domain data into the fine-tuning set, using a very low learning rate, and stopping training before the model overfits to the narrow domain. LoRA is inherently less prone to catastrophic forgetting than full fine-tuning because the base weights remain frozen.
