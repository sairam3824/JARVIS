from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class ChecklistTool(BaseTool):
    definition = ToolDefinition(
        name="checklist",
        description="Creates a checklist preview from comma-separated tasks.",
        input_schema={"objective": {"type": "string"}},
        category="planning",
        capability_tags=["checklists", "daily-activities"],
        result_type="planner",
    )

    def __init__(self, planner_engine, workspace_repository) -> None:
        self.planner_engine = planner_engine
        self.workspace_repository = workspace_repository

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        objective = args.get("objective", "")
        preview = await self.planner_engine.preview("checklist", objective)
        await self.workspace_repository.store_planner_preview(context.session_id, "checklist", preview.title, preview.model_dump())
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=preview.summary,
            structured_output=preview.model_dump(),
            result_type=self.definition.result_type,
            category=self.definition.category,
        )

