# Lab: lab-multi-agent
# Module: ai-agents
# Doc reference: docs/ai-agents/multi-agent-systems.md

import json
import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from shared.config import MODEL, MAX_ITERATIONS, build_client, assert_ollama_ready
from shared.dispatcher import InlineDispatcher
from shared.loop import run_agent
from shared.tools import search_web, read_document, summarize_stub

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ORCHESTRATOR_SYSTEM = (
    "You are a research coordinator. You have access to specialized research agents "
    "for different topics. Delegate research tasks to these agents and synthesize "
    "their results into a final comparative answer. Do not perform domain research "
    "yourself — always delegate to the appropriate agent."
)

SUBAGENT_SYSTEM_TEMPLATE = (
    "You are a specialized research agent for the topic: {topic}. "
    "You have access to web search and document reading tools. "
    "Complete the given research task and return a concise summary of your findings."
)

# Subagent tool declarations (used by each research subagent)
SUBAGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for articles about a topic.",
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
                    "document_id": {"type": "string", "description": "The document ID"},
                },
                "required": ["document_id"],
                "additionalProperties": False,
            },
        },
    },
]

SUBAGENT_DISPATCHER = InlineDispatcher(
    {
        "search_web": search_web,
        "read_document": read_document,
    }
)


# ---------------------------------------------------------------------------
# Subagent implementation
# ---------------------------------------------------------------------------

def make_research_agent(topic: str):
    """
    Returns a callable that runs a research subagent for the given topic.

    Concept: subagent — isolated agent with its own loop, tools, and context.
    The returned function is registered as a tool on the orchestrator.
    """
    def research_agent(query: str) -> str:
        log.info("  [subagent:%s] Starting — query: %s", topic, query)

        # Concept: context isolation — fresh messages list, no orchestrator history
        messages = [
            {
                "role": "system",
                "content": SUBAGENT_SYSTEM_TEMPLATE.format(topic=topic),
            },
            {"role": "user", "content": query},
        ]

        result = run_agent(
            client_ref[0],
            SUBAGENT_TOOLS,
            messages,
            SUBAGENT_DISPATCHER,
            max_iterations=5,
        )

        log.info("  [subagent:%s] Done — result length: %d chars", topic, len(result))
        # Concept: subagent — summarize result before returning to orchestrator
        summary = summarize_stub(result, max_sentences=3)
        return summary

    research_agent.__name__ = f"research_{topic}"
    return research_agent

# Late-bound client reference so subagent closures can use the same client
client_ref: list = [None]


# ---------------------------------------------------------------------------
# Orchestrator tools
# ---------------------------------------------------------------------------

def build_orchestrator_tools(topics: list[str]) -> tuple[list[dict], InlineDispatcher]:
    """Build orchestrator tool declarations and dispatcher for the given topics."""
    tool_declarations = []
    tool_map = {}

    for topic in topics:
        fn = make_research_agent(topic)
        tool_name = f"research_{topic}_agent"
        tool_map[tool_name] = fn

        tool_declarations.append(
            {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": (
                        f"Research agent specialized in {topic}. "
                        f"Searches for and summarizes information about {topic}."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": f"The research question about {topic}",
                            },
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            }
        )

    # Concept: orchestrator — tool set consists only of subagent invocations
    dispatcher = InlineDispatcher(tool_map)
    return tool_declarations, dispatcher


# ---------------------------------------------------------------------------
# Demo 1: orchestrator + subagents
# ---------------------------------------------------------------------------

def demo_orchestration(client) -> None:
    log.info("=" * 60)
    log.info("DEMO 1 — Orchestrator + subagents")
    log.info("Model: %s  |  Max iterations: %d", MODEL, MAX_ITERATIONS)
    log.info("=" * 60)

    task = (
        "Research the Transformer architecture and the RAG technique. "
        "Use the specialized agents for each topic, then write a one-paragraph "
        "comparison of their key technical contributions."
    )
    log.info("Task: %s", task)
    log.info("-" * 60)

    orchestrator_tools, orchestrator_dispatcher = build_orchestrator_tools(
        ["transformer", "rag"]
    )

    messages = [
        {"role": "system", "content": ORCHESTRATOR_SYSTEM},
        {"role": "user", "content": task},
    ]

    # Concept: orchestrator — outer loop delegates to subagents as tool calls
    result = run_agent(
        client,
        orchestrator_tools,
        messages,
        orchestrator_dispatcher,
        max_iterations=MAX_ITERATIONS,
    )

    log.info("-" * 60)
    log.info("ORCHESTRATOR FINAL ANSWER:")
    log.info(result)


# ---------------------------------------------------------------------------
# Demo 2: context isolation verification
# ---------------------------------------------------------------------------

def demo_context_isolation(client) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 2 — Context isolation")
    log.info("=" * 60)
    log.info(
        "Each subagent receives only its own sub-task — not the orchestrator's history."
    )
    log.info(
        "A subagent initialized with the orchestrator's full history (the failure case)"
    )
    log.info("would contaminate the subagent's reasoning with unrelated context.")
    log.info("-" * 60)

    # Run one subagent directly to show its isolated context
    agent_fn = make_research_agent("agent")
    query = "What is the ReAct pattern and how does it combine reasoning with actions?"

    log.info("Running research_agent(topic=agent) directly with isolated context.")
    log.info("Query: %s", query)
    log.info("")

    result = agent_fn(query)

    log.info("-" * 60)
    log.info("Subagent result (summarized, ready for orchestrator):")
    log.info(result)
    log.info("")
    log.info(
        "Observe: the subagent's log shows only its own iterations — "
        "no orchestrator context leaked into its message history."
    )

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - In make_research_agent(), replace the fresh `messages` list with a copy of
    #   the orchestrator's full message history (pass it in via closure)
    # - Observe:
    #   * The subagent reasons about the orchestrator's broader task
    #   * Subagent responses include orchestrator-level context irrelevant to the sub-task
    #   * This shows why context isolation (fresh messages per subagent) is mandatory


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])
    client = build_client()
    client_ref[0] = client

    demo_orchestration(client)
    demo_context_isolation(client)
