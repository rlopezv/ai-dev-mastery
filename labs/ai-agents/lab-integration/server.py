# Lab: lab-integration — MCP server process
# Module: ai-agents
# Doc reference: docs/ai-agents/mcp.md
#
# Identical in structure to lab-mcp-server/server.py.
# Each lab owns its own server.py — no cross-lab file dependencies.

import asyncio
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from shared.tools import search_web, read_document, calculator

server = Server("ai-agents-integration")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_web",
            description="Search the web for articles about a topic.",
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
            description="Evaluate a simple arithmetic expression.",
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
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
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
