from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from models.chat import ChatMessage, ChatRole
from models.contracts import BaseLLMProvider, ToolDefinition


@dataclass(slots=True)
class PlannedToolCall:
    tool_name: str
    args: dict[str, str]
    reason: str
    source: str = "heuristic"


@dataclass(slots=True)
class ToolPlan:
    steps: list[PlannedToolCall] = field(default_factory=list)
    rationale: str = ""
    source: str = "heuristic"


class AgentPlanner:
    def __init__(self, tool_registry, max_steps: int = 3) -> None:
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self._path_pattern = re.compile(
            r"(?P<path>(?:~?/|/)?[\w.\-]+(?:/[\w.\-]+)*\.(?:py|ts|tsx|js|jsx|json|md|txt|csv|yml|yaml))"
        )
        self._quoted_pattern = re.compile(r"[`'\"](?P<value>[^`'\"]+)[`'\"]")

    async def create_plan(self, prompt: str, provider: BaseLLMProvider) -> ToolPlan:
        direct_steps = [
            PlannedToolCall(tool_name=tool_name, args=args, reason="Explicit tool directive.", source="directive")
            for tool_name, args in self.tool_registry.route_prompt(prompt)
        ]
        if direct_steps:
            return ToolPlan(steps=direct_steps[: self.max_steps], rationale="Used direct tool prefixes.", source="directive")

        if not self._likely_needs_tools(prompt):
            return ToolPlan()

        model_plan = await self._plan_with_model(prompt, provider)
        if model_plan.steps:
            return model_plan

        heuristic_steps = self._heuristic_steps(prompt)
        if not heuristic_steps:
            return ToolPlan()
        return ToolPlan(
            steps=heuristic_steps[: self.max_steps],
            rationale="Used local heuristics to decide tool support.",
            source="heuristic",
        )

    async def _plan_with_model(self, prompt: str, provider: BaseLLMProvider) -> ToolPlan:
        tool_manifest = "\n".join(self._tool_manifest_lines())
        system_prompt = (
            "You are a planning layer for JARVIS.\n"
            "Decide if tools should be used before answering the user.\n"
            "Return strict JSON with keys rationale and steps.\n"
            "Each step must include tool_name, args, and reason.\n"
            "Use at most 3 steps.\n"
            "Never select file_system, terminal, code_execution, or app_launcher unless the prompt explicitly asks for that action.\n"
            "If tools are unnecessary, return {\"rationale\":\"...\",\"steps\":[]}."
        )
        planner_request = (
            f"User prompt:\n{prompt}\n\n"
            f"Available tools:\n{tool_manifest}\n\n"
            "Return JSON only."
        )
        try:
            raw_response = await provider.complete_chat(
                [ChatMessage(role=ChatRole.USER, content=planner_request)],
                system_prompt,
            )
        except (ValueError, TypeError, OSError, RuntimeError):
            return ToolPlan()

        parsed = self._extract_json(raw_response)
        if not isinstance(parsed, dict):
            return ToolPlan()

        rationale = str(parsed.get("rationale", "")).strip()
        raw_steps = parsed.get("steps", [])
        if not isinstance(raw_steps, list):
            return ToolPlan()

        steps = self._normalize_steps(prompt, raw_steps, source="model")
        return ToolPlan(steps=steps, rationale=rationale or "Model-selected tool plan.", source="model")

    def _heuristic_steps(self, prompt: str) -> list[PlannedToolCall]:
        lowered = prompt.lower()
        steps: list[PlannedToolCall] = []

        if self._should_search_web(lowered):
            steps.append(
                PlannedToolCall(
                    tool_name="web_search",
                    args={"query": self._extract_search_query(prompt)},
                    reason="Prompt asks for up-to-date or web-based information.",
                )
            )

        if "weather" in lowered or "temperature" in lowered or "visibility" in lowered:
            steps.append(
                PlannedToolCall(
                    tool_name="weather",
                    args={"latitude": "12.97", "longitude": "77.59"},
                    reason="Prompt asks for weather context.",
                )
            )

        if any(
            keyword in lowered
            for keyword in ("checklist", "todo", "to-do", "step-by-step plan", "plan for", "make a plan", "make a checklist")
        ):
            steps.append(
                PlannedToolCall(
                    tool_name="checklist",
                    args={"objective": prompt},
                    reason="Prompt asks for an actionable plan or checklist.",
                )
            )

        if "remember that" in lowered or lowered.startswith("please remember") or lowered.startswith("remember "):
            note = self._after_keyword(prompt, "remember")
            steps.append(
                PlannedToolCall(
                    tool_name="memory_store",
                    args={"note": note or prompt},
                    reason="Prompt asks JARVIS to remember information.",
                )
            )

        if any(keyword in lowered for keyword in ("sentiment", "tone", "emotion")) and "analy" in lowered:
            steps.append(
                PlannedToolCall(
                    tool_name="sentiment",
                    args={"text": prompt},
                    reason="Prompt asks for sentiment or tone analysis.",
                )
            )

        if "qr" in lowered and ("generate" in lowered or "create" in lowered):
            payload = self._extract_quoted_value(prompt) or prompt
            steps.append(
                PlannedToolCall(
                    tool_name="qr",
                    args={"payload_text": payload},
                    reason="Prompt asks to generate a QR code.",
                )
            )

        if "home assistant" in lowered or "smart home" in lowered or lowered.startswith("home status"):
            steps.append(
                PlannedToolCall(
                    tool_name="home_status",
                    args={},
                    reason="Prompt asks for smart-home status.",
                )
            )

        if self._looks_like_csv(prompt):
            steps.append(
                PlannedToolCall(
                    tool_name="analytics",
                    args={"dataset_name": "chat dataset", "kind": "csv", "content": prompt},
                    reason="Prompt contains CSV-style data that can be summarized.",
                )
            )

        file_path = self._extract_file_path(prompt)
        if file_path and self._is_explicit_for_tool(lowered, "file_system"):
            steps.append(
                PlannedToolCall(
                    tool_name="file_system",
                    args={"path": file_path},
                    reason="Prompt explicitly asks to inspect a local file.",
                )
            )

        command = self._extract_command(prompt)
        if command and self._is_explicit_for_tool(lowered, "terminal"):
            steps.append(
                PlannedToolCall(
                    tool_name="terminal",
                    args={"command": command},
                    reason="Prompt explicitly asks to run a shell command.",
                )
            )

        code = self._extract_python_code(prompt)
        if code and self._is_explicit_for_tool(lowered, "code_execution"):
            steps.append(
                PlannedToolCall(
                    tool_name="code_execution",
                    args={"code": code},
                    reason="Prompt explicitly asks to execute Python code.",
                )
            )

        launch_target = self._extract_launch_target(prompt)
        if launch_target and self._is_explicit_for_tool(lowered, "app_launcher"):
            steps.append(
                PlannedToolCall(
                    tool_name="app_launcher",
                    args={"target": launch_target, "mode": "application"},
                    reason="Prompt explicitly asks to open an app.",
                )
            )

        deduped: list[PlannedToolCall] = []
        seen: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
        for step in steps:
            signature = (step.tool_name, tuple(sorted(step.args.items())))
            if signature in seen:
                continue
            seen.add(signature)
            deduped.append(step)
        return deduped

    def _normalize_steps(self, prompt: str, raw_steps: list[Any], source: str) -> list[PlannedToolCall]:
        definitions = {definition.name: definition for definition in self.tool_registry.definitions()}
        lowered = prompt.lower()
        steps: list[PlannedToolCall] = []
        for item in raw_steps[: self.max_steps]:
            if not isinstance(item, dict):
                continue
            tool_name = str(item.get("tool_name", "")).strip()
            definition = definitions.get(tool_name)
            if not definition:
                continue
            args = item.get("args", {})
            if not isinstance(args, dict):
                args = {}
            normalized_args = self._coerce_args(args, definition)
            if definition.requires_confirmation and not self._is_explicit_for_tool(lowered, tool_name):
                continue
            steps.append(
                PlannedToolCall(
                    tool_name=tool_name,
                    args=normalized_args,
                    reason=str(item.get("reason", "Selected by planner.")).strip() or "Selected by planner.",
                    source=source,
                )
            )
        return steps

    def _coerce_args(self, args: dict[str, Any], definition: ToolDefinition) -> dict[str, str]:
        allowed_keys = set(definition.input_schema)
        normalized: dict[str, str] = {}
        for key, value in args.items():
            if allowed_keys and key not in allowed_keys:
                continue
            if value is None:
                continue
            normalized[key] = str(value).strip()
        return normalized

    def _likely_needs_tools(self, prompt: str) -> bool:
        lowered = prompt.lower()
        indicators = (
            "latest",
            "current",
            "today",
            "search",
            "look up",
            "find online",
            "weather",
            "checklist",
            "remember",
            "sentiment",
            "tone",
            "qr",
            "home assistant",
            "smart home",
            "csv",
            "read file",
            "open file",
            "run command",
            "execute",
            "launch",
        )
        return any(indicator in lowered for indicator in indicators) or bool(self._extract_file_path(prompt))

    def _tool_manifest_lines(self) -> list[str]:
        lines = []
        for definition in self.tool_registry.definitions():
            arg_names = ", ".join(definition.input_schema.keys()) or "no args"
            lines.append(
                f"- {definition.name}: {definition.description}; args={arg_names}; "
                f"safety={definition.safety_level.value}; confirm={definition.requires_confirmation}"
            )
        return lines

    def _extract_json(self, raw_response: str) -> Any:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if "\n" in cleaned:
                cleaned = cleaned.split("\n", 1)[1]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    def _should_search_web(self, lowered: str) -> bool:
        web_signals = ("search the web", "look up", "find online", "online", "news", "latest", "current", "recent")
        return any(signal in lowered for signal in web_signals)

    def _extract_search_query(self, prompt: str) -> str:
        cleaned = re.sub(r"(?i)\b(search the web for|search for|look up|find online|latest|current|recent news on)\b", "", prompt)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" :,.")
        return cleaned or prompt

    def _looks_like_csv(self, prompt: str) -> bool:
        if "\n" not in prompt or "," not in prompt:
            return False
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        return len(lines) >= 2 and all("," in line for line in lines[:2])

    def _extract_file_path(self, prompt: str) -> str | None:
        match = self._path_pattern.search(prompt)
        return match.group("path") if match else None

    def _extract_command(self, prompt: str) -> str | None:
        lowered = prompt.lower()
        if "run:" in lowered:
            return prompt.split(":", 1)[-1].strip()
        match = re.search(r"(?i)\b(?:run|execute|use the terminal to run)\b\s+(?P<command>.+)", prompt)
        if not match:
            return None
        command = match.group("command").strip()
        quoted = self._extract_quoted_value(command)
        return quoted or command

    def _extract_python_code(self, prompt: str) -> str | None:
        match = re.search(r"(?i)\b(?:python|execute python|run python)\b\s*:?\s*(?P<code>.+)", prompt, re.DOTALL)
        if not match:
            return None
        code = match.group("code").strip()
        quoted = self._extract_quoted_value(code)
        return quoted or code

    def _extract_launch_target(self, prompt: str) -> str | None:
        match = re.search(r"(?i)\b(?:open|launch)\b\s+(?P<target>[A-Za-z0-9 ._-]+)$", prompt.strip())
        if not match:
            return None
        return match.group("target").strip()

    def _extract_quoted_value(self, text: str) -> str | None:
        match = self._quoted_pattern.search(text)
        return match.group("value").strip() if match else None

    def _after_keyword(self, prompt: str, keyword: str) -> str:
        match = re.search(rf"(?i){re.escape(keyword)}\s*(?:that)?\s*(?P<value>.+)", prompt)
        return match.group("value").strip() if match else ""

    def _is_explicit_for_tool(self, lowered_prompt: str, tool_name: str) -> bool:
        explicit_keywords = {
            "file_system": ("read", "open", "show", "inspect", "file", "contents"),
            "terminal": ("run", "execute", "command", "terminal", "shell"),
            "code_execution": ("python", "code", "script", "execute"),
            "app_launcher": ("open", "launch", "start"),
        }
        keywords = explicit_keywords.get(tool_name)
        if not keywords:
            return True
        return any(keyword in lowered_prompt for keyword in keywords)
