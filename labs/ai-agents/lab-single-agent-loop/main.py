# Lab: lab-single-agent-loop
# Module: ai-agents
# Doc reference: docs/ai-agents/single-agent-loop.md

import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, MAX_ITERATIONS, build_client, assert_ollama_ready
from shared.dispatcher import InlineDispatcher
from shared.loop import run_agent
from shared.tools import search_web, read_document

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a research assistant. You have access to a web search tool and a "
    "document reader. Complete the given research task by using these tools in "
    "sequence. When you have gathered enough information, write your final answer."
)

# Concept: tool registry — declarations passed to the LLM API in tools= parameter
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for articles about a topic. "
                "Returns a numbered list of document IDs and article titles. "
                "Use a document ID with read_document() to get full content."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
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
            "description": (
                "Read the full content of a document by its ID. "
                "Use IDs returned by search_web()."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The document ID from search results",
                    },
                },
                "required": ["document_id"],
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
    }
)


# ---------------------------------------------------------------------------
# Demo 1: normal task completion
# ---------------------------------------------------------------------------

def demo_research(client) -> None:
    log.info("=" * 60)
    log.info("DEMO 1 — Normal task completion")
    log.info("Model: %s  |  Max iterations: %d", MODEL, MAX_ITERATIONS)
    log.info("=" * 60)

    task = (
        "Search for papers about the Transformer architecture, "
        "read the most relevant one, and write a 2-sentence summary "
        "of its key technical contribution."
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
    # - Change max_iterations=MAX_ITERATIONS to max_iterations=1 in the call below
    # - Observe:
    #   * Only one tool call is made (search_web) before the ceiling fires
    #   * Result is "Max iterations reached." instead of a research summary
    #   * The model never gets to call read_document or produce a final answer
    #   * This shows why MAX_ITERATIONS must accommodate the full task length,
    #     not just the first step

    result = run_agent(client, TOOLS, messages, DISPATCHER, max_iterations=MAX_ITERATIONS)

    log.info("-" * 60)
    log.info("FINAL ANSWER:")
    log.info(result)


# ---------------------------------------------------------------------------
# Demo 2: iteration ceiling
# ---------------------------------------------------------------------------

def demo_ceiling(client) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 2 — Iteration ceiling")
    log.info("=" * 60)

    # This task cannot be completed with available stub tools — the agent
    # will search repeatedly, getting the same stub results, until the ceiling fires.
    task = (
        "Find the exact current market capitalization of every S&P 500 company "
        "and rank them in descending order."
    )
    ceiling = 3
    log.info("Task: %s", task)
    log.info("Max iterations: %d  (deliberately low to trigger ceiling)", ceiling)
    log.info("-" * 60)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    # Concept: stop condition — ceiling of 3 forces termination on an unanswerable task
    result = run_agent(client, TOOLS, messages, DISPATCHER, max_iterations=ceiling)

    log.info("-" * 60)
    log.info("Result: %s", result)
    log.info("Expected: 'Max iterations reached.' — stub tools cannot satisfy this task.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])
    client = build_client()

    demo_research(client)
    demo_ceiling(client)
