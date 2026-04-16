from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class LLMRequest:
    """Normalized request object used by all providers."""

    prompt: str
    system: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LLMResponse:
    """Normalized response object returned by all providers."""

    text: str
    model: str
    provider: str
    raw: Any | None = None


class LLMClient(Protocol):
    """Common interface for all LLM providers."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a single text response for the given request."""
        ...
