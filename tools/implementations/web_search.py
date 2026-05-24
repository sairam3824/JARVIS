from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class WebSearchTool(BaseTool):
    definition = ToolDefinition(
        name="web_search",
        description="Searches the public web for up-to-date information.",
        input_schema={"query": {"type": "string"}},
        category="search",
        capability_tags=["google-access", "web-search"],
    )

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        query = args.get("query", "").strip()
        if not query:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="No search query provided.",
                category=self.definition.category,
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output=f"Web search failed: {exc}",
                category=self.definition.category,
            )
        related = payload.get("RelatedTopics", [])[:5]
        lines = []
        for item in related:
            if isinstance(item, dict) and item.get("Text"):
                lines.append(item["Text"])
        output = "\n".join(lines) if lines else payload.get("AbstractText") or "No search results found."
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=output,
            structured_output=payload,
            category=self.definition.category,
        )
