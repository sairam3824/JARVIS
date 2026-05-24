from __future__ import annotations

from models.contracts import ToolDefinition


def build_system_prompt(tool_definitions: list[ToolDefinition], memory_context: str) -> str:
    tool_lines = [
        f"- {tool.name}: {tool.description} (safety={tool.safety_level.value})"
        for tool in tool_definitions
    ]
    tool_block = "\n".join(tool_lines) if tool_lines else "- No tools available."
    return (
        "You are JARVIS, a premium local AI assistant inspired by a cinematic HUD.\n"
        "Be concise, helpful, and operationally aware.\n"
        "You may reference executed tool results already provided in context.\n\n"
        f"Available tools:\n{tool_block}\n\n"
        f"{memory_context}"
    )

