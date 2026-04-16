# Action dispatcher for ai-agents labs
# Doc reference: docs/ai-agents/single-agent-loop.md
#
# Routes tool calls from the model to registered function implementations.
# Errors are returned as strings — never raised — so the agent loop can
# continue and give the model a chance to recover or try a different approach.

import json
import logging
from typing import Callable

log = logging.getLogger(__name__)


class InlineDispatcher:
    """
    Routes tool calls to registered Python functions.

    Concept: action dispatcher — bridges model decisions and runtime execution.
    All results are strings; all errors are strings, not exceptions.
    """

    def __init__(self, tool_map: dict[str, Callable]):
        self._tool_map = tool_map

    def dispatch(self, tool_call) -> str:
        """
        Execute a single tool call and return the result as a string.

        Unknown tools and runtime errors are returned as error strings so the
        agent loop can append them as tool results and let the model recover.
        """
        name = tool_call.function.name
        fn = self._tool_map.get(name)

        # Concept: error-safe dispatch — unknown tool returned as error string
        if fn is None:
            available = list(self._tool_map)
            log.warning("Unknown tool requested: %r. Available: %s", name, available)
            return f"Error: unknown tool '{name}'. Available tools: {available}"

        try:
            args = json.loads(tool_call.function.arguments or "{}")
        except (json.JSONDecodeError, ValueError) as e:
            return f"Error: could not parse arguments for '{name}': {e}"

        try:
            result = fn(**args)
            return str(result)
        except TypeError as e:
            return f"Error: wrong arguments for '{name}': {e}"
        except Exception as e:  # noqa: BLE001
            return f"Error: '{name}' raised {type(e).__name__}: {e}"
