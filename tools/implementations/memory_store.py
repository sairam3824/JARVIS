from __future__ import annotations

from models.contracts import BaseTool, ToolContext, ToolDefinition, ToolExecutionResult


class MemoryStoreTool(BaseTool):
    definition = ToolDefinition(
        name="memory_store",
        description="Stores a note in session memory.",
        input_schema={"note": {"type": "string"}},
        category="memory",
        capability_tags=["history", "memory"],
    )

    def __init__(self, memory_repository=None) -> None:
        self.memory_repository = memory_repository

    async def run(self, context: ToolContext, args: dict[str, str]) -> ToolExecutionResult:
        note = args.get("note", "").strip()
        if not note:
            return ToolExecutionResult(
                tool_name=self.definition.name,
                success=False,
                output="No note content provided.",
                category=self.definition.category,
            )
        if self.memory_repository:
            await self.memory_repository.store_fact(
                session_id=context.session_id,
                content=note,
                kind="user_note",
            )
        return ToolExecutionResult(
            tool_name=self.definition.name,
            success=True,
            output=f"Stored note: {note}",
            category=self.definition.category,
        )
