from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class HomeStatusTool(BaseTool):
    definition = ToolDefinition(
        name="home_status",
        description="Fetches read-only Home Assistant device status and alerts.",
        input_schema={},
        category="integration",
        capability_tags=["smart-home", "home-assistant"],
        result_type="home",
    )

    def __init__(self, home_assistant_adapter, workspace_repository) -> None:
        self.home_assistant_adapter = home_assistant_adapter
        self.workspace_repository = workspace_repository

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        summary = await self.home_assistant_adapter.fetch_status()
        await self.workspace_repository.store_integration_snapshot("home_assistant", summary.model_dump())
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=summary.status == "ok",
            output=summary.alerts[0] if summary.alerts else f"Home Assistant status: {summary.status}",
            structured_output=summary.model_dump(),
            result_type=self.definition.result_type,
            category=self.definition.category,
        )

