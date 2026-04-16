# shared/ — Provider-agnostic LLM client

This package provides a small abstraction layer so a lab can run against:

- **Ollama**
- **OpenAI**
- **OpenAI-compatible providers**
- **Anthropic**

The lab code does not need to know which provider is active. It only calls:

```python
from shared import LLMRequest, build_llm_client
```

and selects the backend through environment variables.

---

## Files

```text
client/
├── __init__.py
├── anthropic_client.py
├── client_factory.py
├── config.py
├── llm_types.py
├── ollama_client.py
└── openai_compatible_client.py
```

---

## Install

This implementation expects:

```bash
pip install requests
```

If your lab already uses a `requirements.txt`, add:

```text
requests>=2.31.0
```

---

## Required configuration

### Option A — Ollama

```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Option B — OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4o-mini
OPENAI_ENDPOINT=https://api.openai.com/v1/chat/completions
```

### Option C — OpenAI-compatible provider

Use this for providers exposing a `/chat/completions`-style API.

```env
LLM_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_PROVIDER_NAME=my-provider
OPENAI_COMPATIBLE_API_KEY=<your-api-key>
OPENAI_COMPATIBLE_MODEL=<provider-model-name>
OPENAI_COMPATIBLE_ENDPOINT=https://provider.example.com/v1/chat/completions
```

### Option D — Anthropic

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<your-api-key>
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
ANTHROPIC_ENDPOINT=https://api.anthropic.com/v1/messages
```

---

## Example usage in a lab

```python
from shared import LLMRequest, build_llm_client


def main() -> None:
    client = build_llm_client()

    request = LLMRequest(
        system="You are a precise classification assistant.",
        prompt=(
            "Classify the topic of this sentence as one of: "
            "economics, sports, technology, politics.\n\n"
            "Sentence: The central bank raised interest rates again."
        ),
        temperature=0.0,
        max_tokens=50,
    )

    response = client.generate(request)

    print(f"Provider: {response.provider}")
    print(f"Model: {response.model}")
    print("--- OUTPUT ---")
    print(response.text)


if __name__ == "__main__":
    main()
```

---

## Example integration inside `labs/<module>/shared/`

Recommended structure:

```text
labs/<module>/shared/
├── __init__.py
├── anthropic_client.py
├── client_factory.py
├── config.py
├── llm_types.py
├── ollama_client.py
└── openai_compatible_client.py
```

Then your lab entry point can do:

```python
from client import LLMRequest, build_llm_client
```

---

## Notes

- This abstraction normalizes **request/response shape**, not model behavior.
- The same prompt may behave differently across providers and models.
- If you switch providers, re-run validation for the lab.
- Keep parsing and validation logic outside the provider clients when possible.
