# Lab: lab-mcp-server
# Module: ai-agents
# Doc reference: docs/ai-agents/mcp.md

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
from shared.tools import search_web, read_document, calculator

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# Path to the MCP server script in the same directory
SERVER_SCRIPT = str(pathlib.Path(__file__).parent / "server.py")

SYSTEM_PROMPT = (
    "You are a research assistant with access to web search, document reading, "
    "and a calculator. Use these tools to complete the given task."
)

RESEARCH_TASK = (
    "Search for papers about the Transformer architecture, "
    "read the most relevant one, and write a 2-sentence summary "
    "of its key technical contribution."
)


# ---------------------------------------------------------------------------
# MCP tool conversion helpers
# ---------------------------------------------------------------------------

def mcp_tool_to_openai(mcp_tool) -> dict:
    """
    Concept: Model Context Protocol — convert MCP tool definition to OpenAI tool format.
    The agent loop and the LLM API are unchanged; only the tool source differs.
    """
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "",
            "parameters": mcp_tool.inputSchema,
        },
    }


# ---------------------------------------------------------------------------
# MCP-backed agent loop
# ---------------------------------------------------------------------------

async def run_agent_with_mcp(session: ClientSession, task: str) -> str:
    """
    Agent loop using MCP for tool dispatch.

    Concept: Model Context Protocol — tools discovered at runtime via tools/list,
    dispatched via tools/call. Loop structure is identical to inline-dispatch version.
    """
    client = build_client()

    # Concept: MCP tools — tool discovery at session startup
    tools_result = await session.list_tools()
    tools = [mcp_tool_to_openai(t) for t in tools_result.tools]

    log.info(
        "MCP session initialized. Discovered %d tools: %s",
        len(tools),
        [t["function"]["name"] for t in tools],
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    # Ceiling-guarded loop — same structure as shared/loop.py
    messages = list(messages)
    for iteration in range(1, MAX_ITERATIONS + 1):
        response = client.chat.completions.create(
            model=MODEL,
            tools=tools,
            messages=messages,
        )
        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

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

        if not msg.tool_calls:
            log.info(
                "[iteration %d] stop — finish_reason=%s, no tool calls",
                iteration,
                finish_reason,
            )
            return msg.content or ""

        log.info("[iteration %d] tool calls: %d", iteration, len(msg.tool_calls))
        for tc in msg.tool_calls:
            log.info("  → tool: %s  args: %s", tc.function.name, tc.function.arguments)
            args = json.loads(tc.function.arguments or "{}")

            # Concept: Model Context Protocol — tool invocation via tools/call
            result_content = await session.call_tool(tc.function.name, args)
            result = result_content.content[0].text if result_content.content else ""

            preview = result[:120] + ("..." if len(result) > 120 else "")
            log.info("  ← result (MCP): %s", preview)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    log.info("Iteration ceiling reached (%d). Stopping.", MAX_ITERATIONS)
    return "Max iterations reached."


# ---------------------------------------------------------------------------
# Demo 1: MCP-based agent
# ---------------------------------------------------------------------------

async def demo_mcp_agent() -> None:
    log.info("=" * 60)
    log.info("DEMO 1 — Agent with MCP tool dispatch")
    log.info("Model: %s  |  Max iterations: %d", MODEL, MAX_ITERATIONS)
    log.info("=" * 60)
    log.info("Task: %s", RESEARCH_TASK)
    log.info("-" * 60)

    server_params = StdioServerParameters(command="python", args=[SERVER_SCRIPT])

    # Concept: MCP server — spawned as subprocess; agent connects via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await run_agent_with_mcp(session, RESEARCH_TASK)

    log.info("-" * 60)
    log.info("FINAL ANSWER (MCP):")
    log.info(result)


# ---------------------------------------------------------------------------
# Demo 2: same task with inline dispatch (for comparison)
# ---------------------------------------------------------------------------

def demo_inline_agent() -> None:
    log.info("")
    log.info("=" * 60)
    log.info("DEMO 2 — Same task with inline dispatch (comparison)")
    log.info("=" * 60)
    log.info("Task: %s", RESEARCH_TASK)
    log.info("-" * 60)

    inline_tools = [
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

    dispatcher = InlineDispatcher({"search_web": search_web, "read_document": read_document})
    client = build_client()

    # --------------------------------------------------
    # FAILURE CASE
    # --------------------------------------------------
    # Failure case:
    # - In demo_mcp_agent(), modify SERVER_SCRIPT to point to a non-existent file
    # - Observe:
    #   * The subprocess fails to start (FileNotFoundError or immediate exit)
    #   * The ClientSession.initialize() call raises a transport error
    #   * The agent cannot run at all — compare with the inline version below which
    #     works without a subprocess
    #   * This shows the process-management dependency that MCP adds

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": RESEARCH_TASK},
    ]

    result = run_agent(client, inline_tools, messages, dispatcher, max_iterations=MAX_ITERATIONS)

    log.info("-" * 60)
    log.info("FINAL ANSWER (inline):")
    log.info(result)
    log.info("")
    log.info(
        "Compare the two answers: same task, same stub tools, same loop — "
        "only the dispatch mechanism differs (MCP subprocess vs. in-process function calls)."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert_ollama_ready(models=[MODEL])

    asyncio.run(demo_mcp_agent())
    demo_inline_agent()
