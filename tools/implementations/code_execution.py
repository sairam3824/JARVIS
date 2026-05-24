from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult, ToolSafetyLevel


class CodeExecutionTool(BaseTool):
    definition = ToolDefinition(
        name="code_execution",
        description="Executes short Python snippets in a temporary file sandbox.",
        input_schema={"code": {"type": "string"}},
        safety_level=ToolSafetyLevel.CONFIRM,
        requires_confirmation=True,
        category="coding",
        capability_tags=["code-generator", "bug-detection"],
    )

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        code = args.get("code", "").strip()
        if not code:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="No code provided.",
                category=self.definition.category,
            )
        with tempfile.TemporaryDirectory(prefix="jarvis-code-") as tmpdir:
            file_path = Path(tmpdir) / "snippet.py"
            file_path.write_text(code, encoding="utf-8")
            proc = await asyncio.create_subprocess_exec(
                "python3",
                str(file_path),
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
                    output="Code execution timed out.",
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
