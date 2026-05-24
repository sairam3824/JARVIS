from __future__ import annotations

from types import SimpleNamespace

import pytest

from agents.orchestrator import AgentOrchestrator
from models.chat import ChatMessage, ChatRequestPayload, ChatRole, ProviderType
from models.contracts import (
    BaseLLMProvider,
    IntentClassification,
    ModelRouteResult,
    SentimentHumorProfile,
    ToolDefinition,
    ToolExecutionResult,
)


class StubProvider(BaseLLMProvider):
    provider_type = ProviderType.OPENROUTER

    async def stream_chat(self, messages, system_prompt):
        if "planning layer" in system_prompt:
            return
        yield "Answer"

    async def complete_chat(self, messages, system_prompt):
        if "planning layer" in system_prompt:
            return (
                '{"rationale":"Need current info first.","steps":['
                '{"tool_name":"web_search","args":{"query":"latest AI assistant news"},"reason":"Fetch current context."}'
                "]}"
            )
        return "Answer"


class ConversationRepositoryStub:
    def __init__(self) -> None:
        self.messages: list[ChatMessage] = []

    async def append_message(self, session_id: str, role: str, content: str, metadata: dict) -> None:
        self.messages.append(ChatMessage(role=ChatRole(role), content=content, metadata=metadata))

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        return list(self.messages)


class MemoryRepositoryStub:
    async def search_relevant(self, prompt: str):
        return []

    async def store_fact(self, session_id: str, content: str) -> None:
        return None


class TraceRepositoryStub:
    def __init__(self) -> None:
        self.records: list[dict] = []

    async def record(self, session_id: str, payload: dict) -> None:
        self.records.append(payload)


class ToolRegistryStub:
    def definitions(self):
        return [
            ToolDefinition(
                name="web_search",
                description="Searches the public web for up-to-date information.",
                input_schema={"query": {"type": "string"}},
                category="search",
            )
        ]

    def route_prompt(self, prompt: str):
        return []

    def get(self, tool_name: str):
        return SimpleNamespace(definition=self.definitions()[0])

    async def execute(self, session_id: str, tool_name: str, args: dict[str, str]):
        return ToolExecutionResult(
            tool_name=tool_name,
            success=True,
            output=f"searched: {args['query']}",
            structured_output={"query": args["query"]},
            category="search",
        )


class TaskRouterStub:
    async def select_route(self, prompt: str, requested_provider: ProviderType | None = None):
        return (
            IntentClassification(intent="general", confidence=0.8, labels=["general"]),
            ModelRouteResult(
                provider=requested_provider or ProviderType.OPENROUTER,
                task="general",
                model_name="stub-model",
                reason="stub",
            ),
        )


class SentimentStub:
    async def score(self, text: str):
        return SentimentHumorProfile(sentiment="neutral", humor_level="low", friendliness=0.5, confidence=0.9)


@pytest.mark.asyncio
async def test_orchestrator_runs_model_selected_tool_plan():
    orchestrator = AgentOrchestrator(
        providers={ProviderType.OPENROUTER: StubProvider()},
        tool_registry=ToolRegistryStub(),
        conversation_repository=ConversationRepositoryStub(),
        memory_repository=MemoryRepositoryStub(),
        trace_repository=TraceRepositoryStub(),
        task_router=TaskRouterStub(),
        sentiment_scorer=SentimentStub(),
    )

    response = await orchestrator.run_chat(
        ChatRequestPayload(
            prompt="What are the latest AI assistant updates?",
            provider=ProviderType.OPENROUTER,
        )
    )

    assert response.message.content == "Answer"
    assert response.tool_results[0]["tool_name"] == "web_search"
    assert response.tool_results[0]["output"] == "searched: latest AI assistant news"
    assert any(entry["type"] == "agent.plan" for entry in response.process_entries)
    assert any(entry["type"] == "agent.step" and entry["label"] == "web_search" for entry in response.process_entries)


@pytest.mark.asyncio
async def test_streaming_done_event_only_includes_new_process_entries():
    orchestrator = AgentOrchestrator(
        providers={ProviderType.OPENROUTER: StubProvider()},
        tool_registry=ToolRegistryStub(),
        conversation_repository=ConversationRepositoryStub(),
        memory_repository=MemoryRepositoryStub(),
        trace_repository=TraceRepositoryStub(),
        task_router=TaskRouterStub(),
        sentiment_scorer=SentimentStub(),
    )
    events: list[dict] = []

    async def emit(event: dict) -> None:
        events.append(event)

    await orchestrator.run_chat(
        ChatRequestPayload(
            prompt="What are the latest AI assistant updates?",
            provider=ProviderType.OPENROUTER,
        ),
        emit=emit,
    )

    done_event = next(event for event in events if event["type"] == "assistant.done")
    process_entries = done_event["payload"]["process_entries"]

    assert any(event["type"] == "intent.detected" for event in events)
    assert any(event["type"] == "model.selected" for event in events)
    assert any(entry["type"] == "agent.plan" for entry in process_entries)
    assert any(entry["type"] == "agent.step" for entry in process_entries)
    assert all(entry["type"] not in {"intent.detected", "model.selected"} for entry in process_entries)
