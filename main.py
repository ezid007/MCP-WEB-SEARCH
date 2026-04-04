#!/usr/bin/env python3
"""
RooCode MCP 서버 - DuckDuckGo 웹 검색 도구
MCP-WEB-SEARCH
이 MCP 서버는 RooCode 에이전트에 웹 검색 기능을 제공합니다.
DuckDuckGo 검색 API 를 사용하여 실시간 웹 검색 결과를 반환합니다.
"""

import json
import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)
from duckduckgo_search import DDGS


# 검색 도구 정의
WEB_SEARCH_TOOL = Tool(
    name="web_search",
    description="웹 검색을 수행하여 관련 정보와 결과를 반환합니다. 질문이나 검색어를 입력받아 DuckDuckGo 에서 검색합니다.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "검색할 쿼리 (예: 'Python 프로그래밍 튜토리얼', '오늘의 날씨 서울')",
            },
            "max_results": {
                "type": "integer",
                "description": "최대 결과 수 (기본값: 10, 최대: 50)",
                "default": 10,
            },
            "region": {
                "type": "string",
                "description": "지역 코드 (예: 'kr-ko' - 한국, 'us-en' - 미국). 기본값: 'kr-ko'",
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
    DuckDuckGo 를 사용하여 웹 검색을 수행합니다.

    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        region: 지역 코드

    Returns:
        검색 결과 목록
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region=region, max_results=max_results))

        # 결과 포맷팅
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                {
                    "rank": i,
                    "title": result.get("title", "제목 없음"),
                    "url": result.get("href", result.get("url", "URL 없음")),
                    "snippet": result.get(
                        "body", result.get("description", "설명 없음")
                    ),
                    "date": result.get("date", "날짜 미제공"),
                }
            )

        return formatted_results
    except Exception as e:
        return [{"error": f"검색 중 오류 발생: {str(e)}"}]


async def handle_tool_call(name: str, arguments: dict) -> CallToolResult:
    """도구 호출을 처리합니다."""
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
                        text="오류: 검색 쿼리가 필요합니다. 'query' 매개변수를 제공해주세요.",
                    )
                ],
            )

        # 검색 수행
        results = perform_web_search(query, max_results, region)

        # 결과 포맷팅
        if not results or (len(results) == 1 and "error" in results[0]):
            error_msg = results[0]["error"] if results else "알 수 없는 오류 발생"
            return CallToolResult(
                success=False,
                content=[TextContent(type="text", text=f"검색 실패: {error_msg}")],
            )

        # 성공적인 결과 포맷팅
        formatted_output = f"🔍 검색 결과: '{query}'\n"
        formatted_output += f"📊 총 {len(results)}개의 결과\n"
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
            content=[TextContent(type="text", text=f"알 수 없는 도구: {name}")],
        )


async def main():
    """MCP 서버 메인 함수."""
    server = Server("roo-code-web-search")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """사용 가능한 도구 목록을 반환합니다."""
        return [WEB_SEARCH_TOOL]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """도구를 호출합니다."""
        result = await handle_tool_call(name, arguments)
        return result.content

    # STDIO 를 통해 MCP 프로토콜 실행
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
