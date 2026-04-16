# Lab: lab-integration
# Module: ai-agents
# Doc reference: docs/ai-agents/architecture.md

import asyncio
import json
import sys
import pathlib
import logging

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from shared.config import MODEL, MAX_ITERATIONS, build_client, assert_ollama_ready
from shared.dispatcher import InlineDispatcher
from shared.loop import run_agent
from shared.tools import search_web, read_document, summarize_stub

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

SERVER_SCRIPT = str(pathlib.Path(__file__).parent / "server.py")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Concept: ReAct pattern — system prompt enforces Thought/Action/Observation traces
REACT_SUBAGENT_SYSTEM = (
    "You are a specialized research agent. Follow this format for every step:\n\n"
    "Thought: [what you know and what you need]\n"
    "Action: [call a tool]\n"
    "Observation: [provided after tool execution]\n\n"
    "When done, write: Final Answer: [your finding]\n"
    "Never skip the Thought step."
)

ORCHESTRATOR_SYSTEM = (
    "You are a research coordinator. You have two specialized research agents. "
    "Delegate sub-tasks to them, then synthesize their results into a final answer. "
    "Do not perform domain research yourself — always delegate. "
    "If a subagent reports an error, note it in your final answer and proceed with "
    "the available results."
)

INLINE_SUBAGENT_TOOLS = [
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
                    "document_id": {"type": "string", "description": "Document ID"},
                },
                "required": ["document_id"],
                "additionalProperties": False,
            },
        },
    },
]

INLINE_DISPATCHER = InlineDispatcher(
    {"search_web": search_web, "read_document": read_document}
)


# ---------------------------------------------------------------------------
# Subagent 1: ReAct agent with inline dispatch
# ---------------------------------------------------------------------------

def react_research_agent(client, topic: str, query: str) -> str:
    """
    Subagent using ReAct pattern with inline tool dispatch.

    Concept: ReAct pattern — Thought/Action/Observation traces visible in message history.
    Concept: subagent — isolated context, specialized for one topic.
    """
    log.info("  [subagent:react:%s] Starting", topic)

    messages = [
        {"role": "system", "content": REACT_SUBAGENT_SYSTEM},
        {"role": "user", "content": query},
    ]

    result = run_agent(client, INLINE_SUBAGENT_TOOLS, messages, INLINE_DISPATCHER, max_iterations=6)
    summary = summarize_stub(result, max_sentences=3)
    log.info("  [subagent:react:%s] Done — %d chars summarized to %d chars", topic, len(result), len(summary))
    return summary


# ---------------------------------------------------------------------------
# Subagent 2: MCP agent
# ---------------------------------------------------------------------------

def mcp_tool_to_openai(mcp_tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.inputSchema,
        },
    }


async def mcp_research_agent(session: ClientSession, topic: str, query: str) -> str:
    """
    Subagent using MCP tool dispatch.

    Concept: Model Context Protocol — same agent loop, tools discovered via tools/list.
    Concept: subagent — isolated context, tools served by MCP subprocess.
    """
    log.info("  [subagent:mcp:%s] Starting", topic)
    client = build_client()

    tools_result = await session.list_tools()
    tools = [mcp_tool_to_openai(t) for t in tools_result.tools]

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a specialized research agent for {topic}. "
                "Complete the research task using your tools."
            ),
        },
        {"role": "user", "content": query},
    ]

    # Ceiling-guarded loop with MCP dispatch
    messages = list(messages)
    for iteration in range(1, 6):
        response = client.chat.completions.create(
            model=MODEL,
            tools=tools,
            messages=messages,
        )
        msg = response.choices[0].message

        assistant_entry: dict = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            assistant_entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        messages.append(assistant_entry)

        if not msg.tool_calls:
            result = msg.content or ""
            summary = summarize_stub(result, max_sentences=3)
            log.info("  [subagent:mcp:%s] Done", topic)
            return summary

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            result_content = await session.call_tool(tc.function.name, args)
            result = result_content.content[0].text if result_content.content else ""
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    log.info("  [subagent:mcp:%s] Ceiling reached", topic)
    return "Max iterations reached."


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

async def run_orchestrator(client, session: ClientSession) -> None:
    """
    Concept: orchestrator — coordinates subagents, synthesizes results.
    Uses both ReAct (inline) and MCP subagents to show full architecture composition.
    """
    main_task = (
        "Research two AI topics: (1) the Transformer architecture, "
        "(2) the ReAct agent pattern. "
        "Use the specialized agents for each topic, then write a comparison of "
        "their key contributions in two sentences."
    )

    log.info("Orchestrator task: %s", main_task)
    log.info("-" * 60)

    # Subagent 1: ReAct agent researches Transformer
    transformer_result = react_research_agent(
        client,
        topic="transformer",
        query="What is the Transformer architecture and what is its key technical contribution?",
    )

    # Subagent 2: MCP agent researches ReAct pattern
    react_result = await mcp_research_agent(
        session,
        topic="react-pattern",
        query="What is the ReAct agent pattern and how does it combine reasoning with actions?",
    )

    log.info("-" * 60)
    log.info("Subagent results received by orchestrator:")
    log.info("  transformer: %s", transformer_result)
    log.info("  react-pattern: %s", react_result)
    log.info("-" * 60)

    # Orchestrator synthesizes results
    synthesis_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ORCHESTRATOR_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Main task: {main_task}\n\n"
                    f"Transformer research summary:\n{transformer_result}\n\n"
                    f"ReAct pattern research summary:\n{react_result}\n\n"
                    "Write a two-sentence comparison."
                ),
            },
        ],
    )
    final_answer = synthesis_response.choices[0].message.content or ""

    log.info("ORCHESTRATOR FINAL ANSWER:")
    log.info(final_answer)


# ---------------------------------------------------------------------------
# Demo: subagent failure handling
# ---------------------------------------------------------------------------

async def demo_failure_handling(client) -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 2 — Subagent failure handling")
    log.info("=" * 60)

    # Simulate a subagent that fails
    def failing_subagent(query: str) -> str:
        return "Error: subagent failed to retrieve results (simulated failure)"

    orchestrator_tools = [
        {
            "type": "function",
            "function": {
                "name": "research_transformer",
                "description": "Research the Transformer architecture.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Research question"},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "research_rag",
                "description": "Research the RAG technique.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Research question"},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
    ]

    def research_transformer(query: str) -> str:
        return summarize_stub(read_document("attention_is_all_you_need"), max_sentences=2)

    # Concept: orchestrator — error propagation: subagent failure returned as error string
    dispatcher = InlineDispatcher(
        {
            "research_transformer": research_transformer,
            "research_rag": failing_subagent,  # simulated failure
        }
    )

    task = (
        "Research both the Transformer architecture and RAG. "
        "If any agent fails, note it and use whatever results are available."
    )

    log.info("Task: %s", task)
    log.info("(research_rag subagent is configured to fail)")
    log.info("-" * 60)

    messages = [
        {"role": "system", "content": ORCHESTRATOR_SYSTEM},
        {"role": "user", "content": task},
    ]

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - Change both subagents to failing_subagent in the dispatcher above
    # - Observe:
    #   * Both subagents return error strings
    #   * The orchestrator receives two error tool results
    #   * The orchestrator's final answer acknowledges both failures
    #   * The loop still terminates cleanly — error strings are valid tool results

    result = run_agent(client, orchestrator_tools, messages, dispatcher, max_iterations=MAX_ITERATIONS)

    log.info("-" * 60)
    log.info("ORCHESTRATOR FINAL ANSWER (with partial failure):")
    log.info(result)
    log.info("")
    log.info(
        "Observe: the orchestrator received an error string from research_rag "
        "and produced a partial answer — the loop did not crash."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    assert_ollama_ready(models=[MODEL])
    client = build_client()

    log.info("=" * 60)
    log.info("DEMO 1 — Full composition: orchestrator + subagents + MCP + ReAct")
    log.info("=" * 60)

    server_params = StdioServerParameters(command="python", args=[SERVER_SCRIPT])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            log.info("MCP session initialized.")
            await run_orchestrator(client, session)

    await demo_failure_handling(client)


if __name__ == "__main__":
    asyncio.run(main())
