from types import SimpleNamespace

from tools.registry import ToolRegistry


def test_tool_registry_routes_prefixed_prompts():
    registry = ToolRegistry(
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

    planned = registry.route_prompt("web: latest AI assistant news")

    assert planned == [("web_search", {"query": "latest AI assistant news"})]
