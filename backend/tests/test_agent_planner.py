from __future__ import annotations

from types import SimpleNamespace

import pytest

from agents.planner import AgentPlanner
from models.chat import ProviderType
from models.contracts import BaseLLMProvider
from tools.registry import ToolRegistry


class StubProvider(BaseLLMProvider):
    provider_type = ProviderType.OPENROUTER

    def __init__(self, response: str) -> None:
        self.response = response

    async def stream_chat(self, messages, system_prompt):
        if False:
            yield ""

    async def complete_chat(self, messages, system_prompt):
        return self.response


def build_registry() -> ToolRegistry:
    return ToolRegistry(
        allowed_roots=["."],
        terminal_timeout=5,
        analytics_service=SimpleNamespace(),
        planner_engine=SimpleNamespace(),
        qr_service=SimpleNamespace(),
        desktop_automation=SimpleNamespace(),
        sentiment_scorer=SimpleNamespace(),
        home_assistant_adapter=SimpleNamespace(),
        workspace_repository=SimpleNamespace(),
    )


@pytest.mark.asyncio
async def test_agent_planner_keeps_directive_prefixes():
    planner = AgentPlanner(build_registry())

    plan = await planner.create_plan("web: latest AI assistant news", StubProvider("not json"))

    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "web_search"
    assert plan.steps[0].args == {"query": "latest AI assistant news"}
    assert plan.source == "directive"


@pytest.mark.asyncio
async def test_agent_planner_uses_heuristics_for_natural_language_requests():
    planner = AgentPlanner(build_registry())

    plan = await planner.create_plan(
        "Search the web for the latest AI assistant launches and make a checklist for evaluation",
        StubProvider("planner unavailable"),
    )

    tool_names = [step.tool_name for step in plan.steps]

    assert "web_search" in tool_names
    assert "checklist" in tool_names
    assert plan.source == "heuristic"


@pytest.mark.asyncio
async def test_agent_planner_filters_confirm_tools_without_explicit_request():
    planner = AgentPlanner(build_registry())
    provider = StubProvider(
        '{"rationale":"inspect workspace","steps":[{"tool_name":"file_system","args":{"path":"README.md"},"reason":"Need repository context."}]}'
    )

    plan = await planner.create_plan("Help the application get the best results", provider)

    assert plan.steps == []


@pytest.mark.asyncio
async def test_agent_planner_allows_explicit_file_reads():
    planner = AgentPlanner(build_registry())

    plan = await planner.create_plan(
        "Please read README.md and summarize it",
        StubProvider("planner unavailable"),
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "file_system"
    assert plan.steps[0].args == {"path": "README.md"}
