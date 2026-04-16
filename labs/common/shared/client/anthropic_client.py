from __future__ import annotations

import requests

from .llm_types import LLMRequest, LLMResponse


class AnthropicClient:
    """Minimal client for Anthropic Messages API-style endpoints."""

    def __init__(self, model: str, api_key: str, endpoint: str) -> None:
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, object] = {
            "model": self.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or 512,
        }
        if request.system:
            payload["system"] = request.system

        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to call Anthropic endpoint {self.endpoint} with model {self.model}: {exc}"
            ) from exc

        data = response.json()
        try:
            content = data["content"]
            text_parts = [
                block["text"]
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            text = "".join(text_parts)
        except (KeyError, TypeError) as exc:
            raise RuntimeError(
                f"Unexpected Anthropic response shape for model {self.model}: {data}"
            ) from exc

        if not text:
            raise RuntimeError(
                f"Anthropic response did not contain text blocks for model {self.model}: {data}"
            )

        return LLMResponse(
            text=text,
            model=self.model,
            provider="anthropic",
            raw=data,
        )
