from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult, ToolSafetyLevel


class AppLauncherTool(BaseTool):
    definition = ToolDefinition(
        name="app_launcher",
        description="Launches a macOS application, URL, or file path using app-specific automation.",
        input_schema={"target": {"type": "string"}, "mode": {"type": "string"}},
        safety_level=ToolSafetyLevel.CONFIRM,
        requires_confirmation=True,
        category="automation",
        capability_tags=["desktop-agent", "open-applications"],
    )

    def __init__(self, desktop_automation) -> None:
        self.desktop_automation = desktop_automation

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        target = args.get("target", "").strip()
        if not target:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="No launch target provided.",
                category=self.definition.category,
            )
        mode = args.get("mode", "application")
        result = await self.desktop_automation.open_target(target, mode=mode)
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=result.get("status") == "launched",
            output=f"Requested launch for {target}.",
            structured_output=result,
            category=self.definition.category,
        )

