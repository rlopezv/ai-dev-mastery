from __future__ import annotations

from dataclasses import asdict

import requests

from .llm_types import LLMRequest, LLMResponse


class OllamaClient:
    """Minimal Ollama client using /api/generate."""

    def __init__(self, model: str, base_url: str) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, request: LLMRequest) -> LLMResponse:
        prompt = request.prompt
        if request.system:
            prompt = f"{request.system}\n\n{request.prompt}"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        if request.max_tokens is not None:
            payload["options"]["num_predict"] = request.max_tokens

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to call Ollama at {self.base_url} with model {self.model}: {exc}"
            ) from exc

        data = response.json()
        text = data.get("response")
        if not isinstance(text, str):
            raise RuntimeError(
                f"Unexpected Ollama response shape for model {self.model}: {data}"
            )

        return LLMResponse(
            text=text,
            model=self.model,
            provider="ollama",
            raw=data,
        )
