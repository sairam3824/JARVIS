from __future__ import annotations

from models.chat import ChatMessage
from models.contracts import MemoryRecord


class ContextMemoryAssembler:
    """Builds compact memory context for a chat run."""

    def assemble(
        self,
        recent_messages: list[ChatMessage],
        recalled_memories: list[MemoryRecord],
    ) -> str:
        recent_lines = [f"{message.role.value}: {message.content}" for message in recent_messages[-6:]]
        memory_lines = [f"- {memory.content}" for memory in recalled_memories[:5]]
        sections = ["Recent conversation:", *recent_lines, "", "Relevant memory:"]
        sections.extend(memory_lines if memory_lines else ["- No stored memory available."])
        return "\n".join(sections)
