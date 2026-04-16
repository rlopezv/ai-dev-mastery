# Canonical agent loop for ai-agents labs
# Doc reference: docs/ai-agents/single-agent-loop.md

import logging
from shared.config import MODEL, MAX_ITERATIONS

log = logging.getLogger(__name__)


def run_agent(
    client,
    tools: list[dict],
    messages: list[dict],
    dispatcher,
    max_iterations: int = MAX_ITERATIONS,
) -> str:
    """
    Ceiling-guarded agent loop.

    Concept: agent loop — perceive (read messages), decide (LLM call),
    act (dispatch tool calls), repeat until stop condition.

    Concept: stop condition — terminates when the model emits no tool calls,
    or when the iteration ceiling is reached (whichever comes first).

    Returns the model's final text response, or "Max iterations reached."
    if the ceiling fires before the model stops on its own.
    """
    # Work on a copy — do not mutate the caller's list
    messages = list(messages)

    for iteration in range(1, max_iterations + 1):
        response = client.chat.completions.create(
            model=MODEL,
            tools=tools,
            messages=messages,
        )
        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Build serialisable assistant entry (SDK objects are not directly reusable)
        assistant_entry: dict = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        messages.append(assistant_entry)

        # Concept: stop condition — absence of tool calls signals the model is done
        # Checking msg.tool_calls (not finish_reason) is robust across providers
        # that may not set finish_reason == "tool_calls" consistently
        if not msg.tool_calls:
            log.info(
                "[iteration %d] stop — finish_reason=%s, no tool calls",
                iteration,
                finish_reason,
            )
            return msg.content or ""

        # Dispatch each tool call and append results before next iteration
        log.info("[iteration %d] tool calls: %d", iteration, len(msg.tool_calls))
        for tc in msg.tool_calls:
            log.info("  → tool: %s  args: %s", tc.function.name, tc.function.arguments)
            result = dispatcher.dispatch(tc)
            preview = result[:120] + ("..." if len(result) > 120 else "")
            log.info("  ← result: %s", preview)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    # Concept: stop condition — ceiling fires when max_iterations is exhausted
    log.info("Iteration ceiling reached (%d). Stopping.", max_iterations)
    return "Max iterations reached."
