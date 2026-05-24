from __future__ import annotations

from pathlib import Path

from models.contracts import ToolContext
from tools.implementations.analytics import AnalyticsTool
from tools.implementations.app_launcher import AppLauncherTool
from tools.implementations.checklist import ChecklistTool
from tools.implementations.code_execution import CodeExecutionTool
from tools.implementations.file_system import FileSystemTool
from tools.implementations.home_status import HomeStatusTool
from tools.implementations.memory_store import MemoryStoreTool
from tools.implementations.qr_tool import QRTool
from tools.implementations.sentiment import SentimentTool
from tools.implementations.terminal import TerminalTool
from tools.implementations.weather import WeatherTool
from tools.implementations.web_search import WebSearchTool


class ToolRegistry:
    def __init__(
        self,
        allowed_roots: list[str],
        terminal_timeout: int,
        *,
        analytics_service,
        planner_engine,
        qr_service,
        desktop_automation,
        sentiment_scorer,
        home_assistant_adapter,
        workspace_repository,
        memory_repository=None,
    ) -> None:
        self.allowed_roots = [Path(root).expanduser().resolve() for root in allowed_roots]
        self.terminal_timeout = terminal_timeout
        self._tools = {
            tool.definition.name: tool
            for tool in [
                WebSearchTool(),
                FileSystemTool(),
                TerminalTool(),
                CodeExecutionTool(),
                MemoryStoreTool(memory_repository),
                AnalyticsTool(analytics_service, workspace_repository),
                AppLauncherTool(desktop_automation),
                ChecklistTool(planner_engine, workspace_repository),
                WeatherTool(),
                SentimentTool(sentiment_scorer),
                QRTool(qr_service, workspace_repository),
                HomeStatusTool(home_assistant_adapter, workspace_repository),
            ]
        }

    def get(self, tool_name: str):
        tool = self._tools.get(tool_name)
        if tool is None:
            raise KeyError(f"Unknown tool: {tool_name}")
        return tool

    def definitions(self):
        return [tool.definition for tool in self._tools.values()]

    async def execute(self, session_id: str, tool_name: str, args: dict[str, str]):
        from models.contracts import ToolExecutionResult

        tool = self.get(tool_name)
        context = ToolContext(
            session_id=session_id,
            allowed_roots=self.allowed_roots,
            metadata={"terminal_timeout": self.terminal_timeout},
        )
        try:
            return await tool.run(context, args)
        except Exception as exc:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                output=f"Tool execution failed: {exc}",
                category=tool.definition.category,
            )

    def route_prompt(self, prompt: str) -> list[tuple[str, dict[str, str]]]:
        lowered = prompt.lower()
        plans: list[tuple[str, dict[str, str]]] = []
        if lowered.startswith("web:"):
            query = prompt.split(":", 1)[-1].strip() if ":" in prompt else prompt
            plans.append(("web_search", {"query": query}))
        if lowered.startswith("file:"):
            plans.append(("file_system", {"path": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("run:"):
            plans.append(("terminal", {"command": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("python:"):
            plans.append(("code_execution", {"code": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("remember:"):
            plans.append(("memory_store", {"note": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("analytics:"):
            plans.append(
                (
                    "analytics",
                    {
                        "dataset_name": "chat analytics",
                        "kind": "csv",
                        "content": prompt.split(":", 1)[-1].strip(),
                    },
                )
            )
        if lowered.startswith("launch:"):
            plans.append(("app_launcher", {"target": prompt.split(":", 1)[-1].strip(), "mode": "application"}))
        if lowered.startswith("checklist:"):
            plans.append(("checklist", {"objective": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("weather:"):
            coords = prompt.split(":", 1)[-1].strip().split(",")
            latitude = coords[0].strip() if coords else "12.97"
            longitude = coords[1].strip() if len(coords) > 1 else "77.59"
            plans.append(("weather", {"latitude": latitude, "longitude": longitude}))
        if lowered.startswith("sentiment:"):
            plans.append(("sentiment", {"text": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("qr:"):
            plans.append(("qr", {"payload_text": prompt.split(":", 1)[-1].strip()}))
        if lowered.startswith("home:"):
            plans.append(("home_status", {}))
        return plans
