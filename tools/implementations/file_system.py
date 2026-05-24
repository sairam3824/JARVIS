from __future__ import annotations

from pathlib import Path

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult, ToolSafetyLevel
from tools.policies.safety import is_path_allowed


class FileSystemTool(BaseTool):
    definition = ToolDefinition(
        name="file_system",
        description="Reads local files from allowed roots.",
        input_schema={"path": {"type": "string"}},
        safety_level=ToolSafetyLevel.CONFIRM,
        requires_confirmation=True,
        category="retrieval",
        capability_tags=["filesystem", "history"],
    )

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        raw_path = args.get("path", "").strip()
        if not raw_path:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="No file path provided.",
                category=self.definition.category,
            )
        target = Path(raw_path).expanduser()
        if not is_path_allowed(target, context.allowed_roots):
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output=f"Path {target} is outside allowed roots.",
                category=self.definition.category,
            )
        if not target.exists():
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output=f"{target} does not exist.",
                category=self.definition.category,
            )
        if target.is_dir():
            entries = sorted(target.iterdir())[:50]
            output = "\n".join(entry.name for entry in entries)
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=True,
                output=output or "(empty directory)",
                structured_output={"path": str(target), "type": "directory"},
                category=self.definition.category,
            )
        try:
            output = target.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError as exc:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output=f"Failed to read {target}: {exc}",
                category=self.definition.category,
            )
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=output,
            structured_output={"path": str(target)},
            category=self.definition.category,
        )
