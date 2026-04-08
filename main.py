#!/usr/bin/env python3
"""
RooCode MCP Server - Web Search Tool with Fallback
MCP-WEB-SEARCH
This MCP server provides web search functionality to RooCode agents.
It uses DuckDuckGo as primary search engine and falls back to Google Custom Search API when rate limited.
"""

import json
import asyncio
import os
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)
from duckduckgo_search import DDGS
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


# Web search tool definition
WEB_SEARCH_TOOL = Tool(
    name="web_search",
    description="Performs web search and returns relevant information and results. Accepts questions or search queries to search on DuckDuckGo.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (e.g., 'Python programming tutorial', 'Today's weather Seoul')",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results (default: 10, max: 50)",
                "default": 10,
            },
            "region": {
                "type": "string",
                "description": "Region code (e.g., 'kr-ko' - Korea, 'us-en' - USA). Default: 'kr-ko'",
                "default": "kr-ko",
            },
        },
        "required": ["query"],
    },
)


def perform_web_search(
    query: str, max_results: int = 10, region: str = "kr-ko"
) -> list[dict[str, Any]]:
    """
    Performs web search using DuckDuckGo with Google Custom Search fallback.

    Args:
        query: Search query
        max_results: Maximum number of results
        region: Region code

    Returns:
        List of search results
    """
    # Try DuckDuckGo first
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region=region, max_results=max_results))

        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                {
                    "rank": i,
                    "title": result.get("title", "No title"),
                    "url": result.get("href", result.get("url", "No URL")),
                    "snippet": result.get(
                        "body", result.get("description", "No description")
                    ),
                    "date": result.get("date", "Date not provided"),
                }
            )

        return formatted_results
    except Exception as e:
        error_msg = str(e)
        # Check if it's a rate limit error
        if "Ratelimit" in error_msg or "202" in error_msg:
            # Fall back to Google Custom Search
            return perform_google_search(query, max_results)
        return [{"error": f"Error during search: {str(e)}"}]


def perform_google_search(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Performs web search using Google Custom Search API.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of search results
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return [{"error": "Google API credentials not configured. Please set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file."}]

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        cse = service.cse()
        result = cse.list(q=query, cx=GOOGLE_CSE_ID, num=min(max_results, 10)).execute()

        formatted_results = []
        for i, item in enumerate(result.get("items", []), 1):
            formatted_results.append(
                {
                    "rank": i,
                    "title": item.get("title", "No title"),
                    "url": item.get("link", "No URL"),
                    "snippet": item.get("snippet", "No description"),
                    "date": "Date not provided",
                }
            )

        return formatted_results
    except Exception as e:
        return [{"error": f"Google search failed: {str(e)}"}]


async def handle_tool_call(name: str, arguments: dict) -> CallToolResult:
    """Handles tool calls."""
    if name == "web_search":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)
        region = arguments.get("region", "kr-ko")

        if not query:
            return CallToolResult(
                success=False,
                content=[
                    TextContent(
                        type="text",
                        text="Error: Search query is required. Please provide the 'query' parameter.",
                    )
                ],
            )

        # 검색 수행
        results = perform_web_search(query, max_results, region)

        # Format results
        if not results or (len(results) == 1 and "error" in results[0]):
            error_msg = results[0]["error"] if results else "Unknown error occurred"
            return CallToolResult(
                success=False,
                content=[TextContent(type="text", text=f"Search failed: {error_msg}")],
            )

        # Format successful results
        formatted_output = f"🔍 Search results: '{query}'\n"
        formatted_output += f"📊 Total {len(results)} results\n"
        formatted_output += "=" * 50 + "\n\n"

        for result in results:
            formatted_output += f"📌 {result['rank']}. {result['title']}\n"
            formatted_output += f"   🔗 {result['url']}\n"
            formatted_output += f"   📝 {result['snippet']}\n"
            formatted_output += f"   📅 {result['date']}\n\n"

        return CallToolResult(
            success=True,
            content=[
                TextContent(type="text", text=formatted_output),
                TextContent(
                    type="text", text=json.dumps(results, ensure_ascii=False, indent=2)
                ),
            ],
        )
    else:
        return CallToolResult(
            success=False,
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
        )


async def main():
    """MCP server main function."""
    server = Server("roo-code-web-search")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Returns list of available tools."""
        return [WEB_SEARCH_TOOL]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Calls a tool."""
        result = await handle_tool_call(name, arguments)
        return result.content

    # Run MCP protocol via STDIO
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
