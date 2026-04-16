# Shared: conversation history manager
# Doc reference: docs/memory-context/conversation-history.md

from dataclasses import dataclass, field
from shared.config import count_tokens, HISTORY_BUDGET, COMPRESSION_THRESHOLD


@dataclass
class HistoryManager:
    """
    Accumulates conversation turns, tracks token count, and signals when the
    compression threshold is reached.

    Concept: conversation history — a flat list of role/content dicts passed to
    the LLM on every call. Token count grows with each turn.
    """

    budget: int = HISTORY_BUDGET
    threshold: int = COMPRESSION_THRESHOLD
    _history: list[dict] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Read access
    # ------------------------------------------------------------------

    @property
    def history(self) -> list[dict]:
        """Return a copy of the current history list."""
        return list(self._history)

    @property
    def token_count(self) -> int:
        """Concept: token counting — approximate cost of the current history."""
        return count_tokens(self._history)

    @property
    def budget_remaining(self) -> int:
        return self.budget - self.token_count

    @property
    def at_threshold(self) -> bool:
        """
        Concept: compression threshold — True when history exceeds 80% of budget.
        Signals the caller to apply a context management strategy before the
        next API call.
        """
        return self.token_count >= self.threshold

    @property
    def at_ceiling(self) -> bool:
        """True when history is at or above the hard budget ceiling."""
        return self.token_count >= self.budget

    # ------------------------------------------------------------------
    # Write access
    # ------------------------------------------------------------------

    def add_user(self, content: str) -> None:
        self._history.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self._history.append({"role": "assistant", "content": content})

    def replace(self, new_history: list[dict]) -> None:
        """Replace the full history list (used after compression or truncation)."""
        self._history = list(new_history)

    def reset(self) -> None:
        """Clear all history."""
        self._history = []

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def status_line(self) -> str:
        return (
            f"tokens: {self.token_count} / {self.budget} "
            f"(remaining: {self.budget_remaining}) "
            f"| {'THRESHOLD' if self.at_threshold else 'ok'}"
        )
