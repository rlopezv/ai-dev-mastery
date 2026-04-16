from __future__ import annotations

import os


def require_env(name: str) -> str:
    """Return an environment variable or raise a clear error."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_env(name: str, default: str | None = None) -> str | None:
    """Return an environment variable or a default value."""
    return os.getenv(name, default)
