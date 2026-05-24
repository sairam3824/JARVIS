from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class AnalyticsTool(BaseTool):
    definition = ToolDefinition(
        name="analytics",
        description="Computes dataset statistics from structured text or CSV content.",
        input_schema={"dataset_name": {"type": "string"}, "content": {"type": "string"}, "kind": {"type": "string"}},
        category="analytics",
        capability_tags=["statistics", "insights"],
        result_type="analytics",
    )

    def __init__(self, analytics_service, workspace_repository) -> None:
        self.analytics_service = analytics_service
        self.workspace_repository = workspace_repository

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        dataset_name = args.get("dataset_name", "ad-hoc dataset")
        kind = args.get("kind", "csv")
        content = args.get("content", "")
        summary = await self.analytics_service.summarize_text_dataset(dataset_name, content, kind)
        dataset_id = await self.workspace_repository.store_dataset(dataset_name, kind, content, {"tool_run": True})
        await self.workspace_repository.record_analysis("dataset", dataset_id, "tool_analytics", summary.model_dump())
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=summary.insights[0] if summary.insights else "Analytics complete.",
            structured_output=summary.model_dump(),
            result_type=self.definition.result_type,
            category=self.definition.category,
        )

