# Transformer Architecture

If you want to understand why large language models work the way they do, the transformer is the place to start. Introduced in 2017 in the paper "Attention Is All You Need", it replaced older recurrent architectures and became the foundation of almost every modern language model — GPT, LLaMA, Claude, and Gemini all build on the same core design.

## The Attention Mechanism

The key insight behind the transformer is that when processing a word, not all other words in the sentence are equally relevant. A verb depends strongly on its subject; a pronoun depends on its antecedent. The **self-attention mechanism** formalises this intuition: for each token, the model learns to assign a relevance weight to every other token in the sequence and computes a weighted combination of their representations.

Technically, each token is projected into three vectors — Query, Key, and Value. The attention score between two tokens is the dot product of one token's Query with the other's Key, divided by the square root of the key dimension to prevent the dot products from growing too large, then passed through a softmax to produce a probability distribution. The output for each token is the weighted sum of all Value vectors, using those probabilities as weights.

**Multi-head attention** runs this operation several times in parallel with independent learned projections — typically 12 to 32 heads in modern models. The outputs are concatenated and projected back to the model dimension. Running multiple heads allows the model to track different types of relationships simultaneously: one head may attend to syntactic dependencies, another to coreference, another to positional proximity.

## Feed-Forward Layers

After attention, each token's representation passes through a **feed-forward network** applied independently to every position. It consists of two linear transformations with a nonlinearity (GELU or ReLU) between them. The first layer expands the representation to four times the model dimension, and the second projects it back. Despite their simplicity, these layers store the majority of a model's factual knowledge — ablation studies show that factual recall degrades sharply when feed-forward weights are suppressed.

## Residual Connections and Layer Normalisation

Each sub-layer — attention and feed-forward — wraps its computation in a **residual connection**: the input is added to the output before passing to the next layer. This preserves the original signal through many stacked layers and keeps gradients stable during training. **Layer normalisation** is applied either before or after each sub-layer to keep activations in a well-behaved range. Most modern models use pre-normalisation (before the sub-layer), which improves training stability.

## Positional Encoding

Transformers process all tokens in parallel, so they have no built-in sense of sequence order. **Positional encodings** add position-dependent vectors to token embeddings before the first layer. The original paper used fixed sinusoidal functions; later models learned positional embeddings from data. Modern architectures like LLaMA use **Rotary Position Embedding (RoPE)**, which encodes relative position by rotating the Query and Key vectors in the attention computation — this generalises better to sequence lengths not seen during training.

## The KV Cache

At inference time, a decoder-only transformer generates one token per forward pass. Without optimisation, each step would recompute the Key and Value tensors for every previous token — an O(n²) total cost for a response of length n. The **KV cache** stores these tensors from previous steps so only the new token needs to be processed each time, reducing the cost to roughly O(n). This is why context window size directly affects memory requirements: a 128k-token context window requires storing KV tensors for 128,000 positions throughout generation.

## Scaling

Transformer performance follows predictable scaling laws: capability improves as a power law of model size, training data, and compute budget. A 7-billion-parameter model at 4-bit quantisation requires around 4 GB of VRAM and runs on a consumer GPU. The architectural pattern is identical at all scales — larger models have more layers, wider dimensions, and more attention heads, but the same fundamental components.
