from __future__ import annotations

import requests

from .llm_types import LLMRequest, LLMResponse


class OpenAICompatibleClient:
    """
    Generic client for OpenAI-compatible chat completion endpoints.

    Works with providers that expose a /chat/completions-style API.
    """

    def __init__(self, provider: str, model: str, api_key: str, endpoint: str) -> None:
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint

    def generate(self, request: LLMRequest) -> LLMResponse:
        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.append({"role": "user", "content": request.prompt})

        payload: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to call {self.provider} at {self.endpoint} with model {self.model}: {exc}"
            ) from exc

        data = response.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected OpenAI-compatible response shape from {self.provider}: {data}"
            ) from exc

        return LLMResponse(
            text=text,
            model=self.model,
            provider=self.provider,
            raw=data,
        )
