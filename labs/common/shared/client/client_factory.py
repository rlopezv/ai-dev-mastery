from __future__ import annotations

from .anthropic_client import AnthropicClient
from .config import get_env, require_env
from .llm_types import LLMClient
from .ollama_client import OllamaClient
from .openai_compatible_client import OpenAICompatibleClient


def build_llm_client() -> LLMClient:
    """
    Build an LLM client based on LLM_PROVIDER.

    Supported values:
    - ollama
    - openai
    - openai_compatible
    - anthropic
    """
    provider = (get_env("LLM_PROVIDER", "ollama") or "ollama").lower()

    if provider == "ollama":
        return OllamaClient(
            model=get_env("OLLAMA_MODEL", "llama3.2") or "llama3.2",
            base_url=get_env("OLLAMA_URL", "http://localhost:11434") or "http://localhost:11434",
        )

    if provider == "openai":
        return OpenAICompatibleClient(
            provider="openai",
            model=get_env("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
            api_key=require_env("OPENAI_API_KEY"),
            endpoint=get_env("OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions")
            or "https://api.openai.com/v1/chat/completions",
        )

    if provider == "openai_compatible":
        return OpenAICompatibleClient(
            provider=get_env("OPENAI_COMPATIBLE_PROVIDER_NAME", "openai_compatible")
            or "openai_compatible",
            model=require_env("OPENAI_COMPATIBLE_MODEL"),
            api_key=require_env("OPENAI_COMPATIBLE_API_KEY"),
            endpoint=require_env("OPENAI_COMPATIBLE_ENDPOINT"),
        )

    if provider == "anthropic":
        return AnthropicClient(
            model=get_env("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
            or "claude-3-5-sonnet-latest",
            api_key=require_env("ANTHROPIC_API_KEY"),
            endpoint=get_env("ANTHROPIC_ENDPOINT", "https://api.anthropic.com/v1/messages")
            or "https://api.anthropic.com/v1/messages",
        )

    raise ValueError(
        "Unsupported LLM_PROVIDER. Use one of: ollama, openai, openai_compatible, anthropic."
    )
