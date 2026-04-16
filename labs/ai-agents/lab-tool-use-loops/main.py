# Lab: lab-tool-use-loops
# Module: ai-agents
# Doc reference: docs/ai-agents/tool-use-loops.md

import json
import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, MAX_ITERATIONS, build_client, assert_ollama_ready
from shared.dispatcher import InlineDispatcher
from shared.tools import search_web, read_document, calculator

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a research assistant with access to web search, document reading, "
    "and a calculator. Use these tools to complete the given task. "
    "When you have all the information you need, write your final answer."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for articles about a topic. "
                "Returns a numbered list of document IDs and titles."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": "Read the full content of a document by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "The document ID from search results"},
                },
                "required": ["document_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a simple arithmetic expression. Supports +, -, *, / and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Arithmetic expression to evaluate"},
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]

# Concept: action dispatcher — maps tool names to implementations
DISPATCHER = InlineDispatcher(
    {
        "search_web": search_web,
        "read_document": read_document,
        "calculator": calculator,
    }
)


# ---------------------------------------------------------------------------
# Instrumented agent loop — extends the shared loop with accumulation tracing
# ---------------------------------------------------------------------------

def run_agent_instrumented(client, tools, messages, dispatcher, max_iterations=MAX_ITERATIONS):
    """
    Agent loop that prints the message accumulation protocol explicitly.

    Concept: tool-use loop — shows role sequence and tool_call_id matching
    at each iteration so the protocol is directly observable.
    """
    # Work on a copy
    messages = list(messages)

    for iteration in range(1, max_iterations + 1):
        response = client.chat.completions.create(
            model=MODEL,
            tools=tools,
            messages=messages,
        )
        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Concept: tool result accumulation — per-iteration token count
        usage = response.usage
        if usage:
            log.info(
                "[iteration %d] tokens: prompt=%d  completion=%d  total=%d",
                iteration,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
            )

        # Concept: message accumulator — Rule 1: append assistant message BEFORE tool results
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
        messages.append(assistant_entry)  # Rule 1: assistant first

        if not msg.tool_calls:
            log.info(
                "[iteration %d] stop — finish_reason=%s, no tool calls",
                iteration,
                finish_reason,
            )
            return msg.content or "", messages

        # Concept: tool result accumulation — Rule 2: one result per call
        n = len(msg.tool_calls)
        names = [tc.function.name for tc in msg.tool_calls]
        if n > 1:
            # Concept: tool result accumulation — parallel tool calls
            log.info(
                "[iteration %d] Dispatching %d tools in parallel: %s",
                iteration,
                n,
                names,
            )
        else:
            log.info("[iteration %d] tool call: %s", iteration, names[0])

        for tc in msg.tool_calls:
            log.info("  → %s  args: %s", tc.function.name, tc.function.arguments)
            result = dispatcher.dispatch(tc)
            preview = result[:100] + ("..." if len(result) > 100 else "")
            log.info("  ← result [id=%s]: %s", tc.id[:8], preview)
            # Rule 2 + Rule 3: append each result with matching tool_call_id
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )
        # Rule 3: all results appended before next LLM call (loop continues)

    log.info("Iteration ceiling reached (%d). Stopping.", max_iterations)
    return "Max iterations reached.", messages


# ---------------------------------------------------------------------------
# History printer
# ---------------------------------------------------------------------------

def print_message_history(messages: list[dict]) -> None:
    """Print the message accumulator contents showing the role sequence."""
    log.info("")
    log.info("MESSAGE HISTORY (%d messages):", len(messages))
    for i, m in enumerate(messages):
        role = m["role"]
        content_preview = (m.get("content") or "")[:60]
        if role == "assistant" and m.get("tool_calls"):
            calls = [tc["function"]["name"] for tc in m["tool_calls"]]
            log.info("  [%02d] %-10s → tool_calls: %s", i, role, calls)
        elif role == "tool":
            log.info(
                "  [%02d] %-10s  id=%s  content: %s",
                i,
                role,
                m.get("tool_call_id", "")[:8],
                content_preview,
            )
        else:
            log.info("  [%02d] %-10s  %s", i, role, content_preview)


# ---------------------------------------------------------------------------
# Demo 1: sequential tool use — search then read
# ---------------------------------------------------------------------------

def demo_sequential(client) -> None:
    log.info("=" * 60)
    log.info("DEMO 1 — Sequential tool use (search → read)")
    log.info("=" * 60)

    task = (
        "Search for papers about RAG (retrieval-augmented generation), "
        "read the main RAG paper, and summarize its key contribution in one sentence."
    )
    log.info("Task: %s", task)
    log.info("-" * 60)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - In run_agent_instrumented(), move messages.append(assistant_entry) to AFTER
    #   the tool results loop (violating Rule 1)
    # - Observe:
    #   * The API returns a validation error: tool result has no matching assistant message
    #   * Or the model sees tool results before the call that generated them
    #   * This shows why Rule 1 (assistant message first) is mandatory

    result, final_messages = run_agent_instrumented(
        client, TOOLS, messages, DISPATCHER, max_iterations=MAX_ITERATIONS
    )

    log.info("-" * 60)
    log.info("FINAL ANSWER: %s", result)
    print_message_history(final_messages)


# ---------------------------------------------------------------------------
# Demo 2: parallel tool call scenario
# ---------------------------------------------------------------------------

def demo_parallel(client) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 2 — Parallel tool calls")
    log.info("=" * 60)

    task = (
        "At the same time: calculate 128 * 256, and search for papers about "
        "the Transformer architecture. Report both results."
    )
    log.info("Task: %s", task)
    log.info("(Model may call calculator and search_web in the same turn.)")
    log.info("-" * 60)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    result, final_messages = run_agent_instrumented(
        client, TOOLS, messages, DISPATCHER, max_iterations=MAX_ITERATIONS
    )

    log.info("-" * 60)
    log.info("FINAL ANSWER: %s", result)
    print_message_history(final_messages)
    log.info("")
    log.info(
        "Observe: if 'Dispatching 2 tools in parallel' appeared above, "
        "Rule 2 (one result per call) and Rule 3 (all results before re-call) were exercised."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])
    client = build_client()

    demo_sequential(client)
    demo_parallel(client)
