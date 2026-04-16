# LLM Inference

Generating a response from a language model is more involved than it might appear. The model does not produce the entire response in one step — it generates one token at a time, and the mechanics of that process determine the latency, cost, and quality you observe in practice. Understanding inference helps you make better decisions about model selection, prompt design, and production architecture.

## Autoregressive Generation

Decoder-only language models produce tokens one at a time. Each forward pass takes the full input sequence and outputs a probability distribution over the vocabulary for the next token. A token is sampled from that distribution, appended to the sequence, and the process repeats. This is called **autoregressive generation**.

The practical consequence is that total generation time grows linearly with output length. Generating 200 tokens takes approximately twice as long as generating 100 tokens, holding input length constant. This is why `max_tokens` is an important parameter — setting it too high reserves generation capacity that may never be used, and on some APIs, even unused token reservations affect cost.

## The KV Cache

Without optimisation, each autoregressive step would require recomputing the attention Key and Value tensors for every previous token in the sequence — an O(n²) total cost for a response of n tokens. The **KV cache** eliminates this by storing the Key and Value tensors computed in the prefill step (processing the input prompt) and in each generation step. On subsequent steps, only the newly generated token needs to be processed; all previous KV tensors are read from cache. This reduces the marginal cost per generated token from O(n) to roughly constant.

The trade-off is memory: the KV cache grows with sequence length and model size. For a 7B-parameter model with a 128k-token context window, the KV cache alone can occupy several gigabytes of VRAM. This is why longer context windows require more memory even when the actual input is short — the cache must be pre-allocated.

## Inference Parameters

The probability distribution over the next token can be shaped by several parameters:

**Temperature** rescales the logits (raw model scores) before the softmax that converts them to probabilities. A temperature below 1.0 sharpens the distribution toward the highest-probability token; above 1.0 flattens it, making lower-probability tokens more likely. Temperature 0.0 is equivalent to always selecting the argmax — deterministic but prone to repetition on longer outputs.

**Top-k** restricts sampling to the k tokens with the highest probability, zeroing out all others before re-normalising. **Top-p** (nucleus sampling) retains the smallest set of tokens whose cumulative probability reaches a threshold p — the candidate pool shrinks automatically when the distribution is peaked and expands when it is flat.

## Latency: Two Components

Response latency has two distinct parts. **Time to first token (TTFT)** is the delay between sending the request and receiving the first output token — it covers processing the entire input prompt in a single parallel forward pass. TTFT grows with prompt length. **Inter-token latency** is the time between consecutive output tokens; it is roughly constant per token and scales with model size and hardware throughput.

In streaming mode, the user sees output as soon as TTFT elapses, which is why streaming feels responsive even for long completions. In non-streaming mode, the caller waits for the entire response before receiving anything.

## Quantisation

Model weights are normally stored as 16-bit floats (FP16 or BF16). **Quantisation** reduces this to 8-bit integers (INT8) or 4-bit integers (INT4), cutting memory and memory-bandwidth requirements by two to four times respectively. A 7-billion-parameter model at 4-bit quantisation requires approximately 4 GB of VRAM and runs on a consumer GPU. The accuracy cost is modest — typically 1–3 percentage points on standard benchmarks — and is usually acceptable for inference. Ollama applies 4-bit quantisation by default when serving models locally.
