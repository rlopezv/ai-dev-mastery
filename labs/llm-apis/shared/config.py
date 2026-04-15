# Shared configuration loader
# Module: llm-apis
# Doc reference: docs/llm-apis/implementation-reference.md

import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")

OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "500"))
