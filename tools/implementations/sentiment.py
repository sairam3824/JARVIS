from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class SentimentTool(BaseTool):
    definition = ToolDefinition(
        name="sentiment",
        description="Scores text for sentiment and humor level.",
        input_schema={"text": {"type": "string"}},
        category="context",
        capability_tags=["sentiment-analysis", "humor-levels"],
        result_type="sentiment",
    )

    def __init__(self, sentiment_scorer) -> None:
        self.sentiment_scorer = sentiment_scorer

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        text = args.get("text", "")
        profile = await self.sentiment_scorer.score(text)
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=f"{profile.sentiment} sentiment with {profile.humor_level} humor.",
            structured_output=profile.model_dump(),
            result_type=self.definition.result_type,
            category=self.definition.category,
        )

