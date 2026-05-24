from __future__ import annotations

import asyncio

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult, ToolSafetyLevel


class TerminalTool(BaseTool):
    definition = ToolDefinition(
        name="terminal",
        description="Runs a local shell command with timeout and output capture.",
        input_schema={"command": {"type": "string"}},
        safety_level=ToolSafetyLevel.CONFIRM,
        requires_confirmation=True,
        category="automation",
        capability_tags=["terminal", "desktop-agent"],
    )

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        command = args.get("command", "").strip()
        if not command:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="No command provided.",
                category=self.definition.category,
            )
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        timeout = float(context.metadata.get("terminal_timeout", 15))
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="Command timed out.",
                category=self.definition.category,
            )
        output = stdout.decode("utf-8", errors="ignore")[:4000]
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=proc.returncode == 0,
            output=output,
            structured_output={"returncode": proc.returncode},
            category=self.definition.category,
        )
