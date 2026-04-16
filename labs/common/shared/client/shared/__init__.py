"""Shared LLM client abstraction for labs."""
from .llm_types import LLMRequest, LLMResponse, LLMClient
from .client_factory import build_llm_client

__all__ = ["LLMRequest", "LLMResponse", "LLMClient", "build_llm_client"]
