# Lab: lab-mcp-server — MCP server process
# Module: ai-agents
# Doc reference: docs/ai-agents/mcp.md
#
# Run directly to diagnose startup errors: python server.py
# In normal use, main.py spawns this as a subprocess via stdio.

import asyncio
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from shared.tools import search_web, read_document, calculator

# Concept: MCP server — exposes tools via the MCP protocol over stdio
server = Server("ai-agents-lab")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    Concept: MCP tools — tool discovery endpoint; agents call tools/list at startup.
    Returns the same three tools available in the inline-dispatch labs.
    """
    return [
        types.Tool(
            name="search_web",
            description=(
                "Search the web for articles about a topic. "
                "Returns a numbered list of document IDs and article titles."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="read_document",
            description="Read the full content of a document by its ID.",
            inputSchema={
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
        ),
        types.Tool(
            name="calculator",
            description="Evaluate a simple arithmetic expression. Supports +, -, *, / and parentheses.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The arithmetic expression to evaluate",
                    },
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        ),
    ]


@server.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """
    Concept: MCP tools — tool invocation endpoint; routes to stub implementations.
    Returns results as TextContent (string-typed), matching the tool-use loop protocol.
    """
    if name == "search_web":
        result = search_web(**arguments)
    elif name == "read_document":
        result = read_document(**arguments)
    elif name == "calculator":
        result = calculator(**arguments)
    else:
        result = f"Error: unknown tool '{name}'"

    return [types.TextContent(type="text", text=result)]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
