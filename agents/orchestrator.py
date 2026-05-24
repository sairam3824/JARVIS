from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from agents.memory import ContextMemoryAssembler
from agents.planner import AgentPlanner
from agents.policies import build_system_prompt
from models.chat import ChatMessage, ChatRequestPayload, ChatResponsePayload, ChatRole, ProviderType
from models.contracts import BaseLLMProvider
from models.events import SocketEventType, make_event
from tools.registry import ToolRegistry

EmitFn = Callable[[dict[str, Any]], Awaitable[None]]


class AgentOrchestrator:
    def __init__(
        self,
        providers: dict[ProviderType, BaseLLMProvider],
        tool_registry: ToolRegistry,
        conversation_repository,
        memory_repository,
        trace_repository,
        task_router,
        sentiment_scorer,
    ) -> None:
        self.providers = providers
        self.tool_registry = tool_registry
        self.conversation_repository = conversation_repository
        self.memory_repository = memory_repository
        self.trace_repository = trace_repository
        self.task_router = task_router
        self.sentiment_scorer = sentiment_scorer
        self.memory_assembler = ContextMemoryAssembler()
        self.agent_planner = AgentPlanner(tool_registry)

    async def run_chat(
        self,
        request: ChatRequestPayload,
        emit: EmitFn | None = None,
    ) -> ChatResponsePayload:
        session_id = request.session_id or str(uuid.uuid4())
        intent_result, route_result = await self.task_router.select_route(request.prompt, request.provider)
        provider_type = route_result.provider
        provider = self.providers[provider_type]
        sentiment_profile = await self.sentiment_scorer.score(request.prompt)
        process_entries = [
            {
                "type": SocketEventType.INTENT_DETECTED.value,
                "label": intent_result.intent,
                "detail": f"confidence={intent_result.confidence:.2f}",
            },
            {
                "type": SocketEventType.MODEL_SELECTED.value,
                "label": route_result.provider.value,
                "detail": route_result.reason,
            },
        ]

        await self.conversation_repository.append_message(
            session_id=session_id,
            role=ChatRole.USER.value,
            content=request.prompt,
            metadata={
                "voice_mode": request.voice_mode,
                "intent": intent_result.intent,
                "sentiment": sentiment_profile.sentiment,
                "humor_level": sentiment_profile.humor_level,
            },
        )
        if emit:
            await emit(make_event(SocketEventType.SESSION_STARTED, session_id=session_id).model_dump(mode="json"))
            await emit(
                make_event(
                    SocketEventType.INTENT_DETECTED,
                    session_id=session_id,
                    intent=intent_result.intent,
                    confidence=intent_result.confidence,
                    labels=intent_result.labels,
                ).model_dump(mode="json")
            )
            await emit(
                make_event(
                    SocketEventType.MODEL_SELECTED,
                    session_id=session_id,
                    provider=route_result.provider.value,
                    model_name=route_result.model_name,
                    reason=route_result.reason,
                ).model_dump(mode="json")
            )

        history = await self.conversation_repository.get_messages(session_id)
        memories = await self.memory_repository.search_relevant(request.prompt)
        memory_context = self.memory_assembler.assemble(history, memories)

        tool_results, agent_process_entries = await self._maybe_run_tools(session_id, request.prompt, provider, emit)
        process_entries.extend(agent_process_entries)
        prompt_with_tools = list(history)
        if tool_results:
            prompt_with_tools.extend(
                [
                    ChatMessage(
                        role=ChatRole.TOOL,
                        content=self._format_tool_result(result),
                        metadata={"tool_result": result.model_dump()},
                    )
                    for result in tool_results
                ]
            )

        system_prompt = build_system_prompt(self.tool_registry.definitions(), memory_context)
        system_prompt += (
            f"\n\nDetected intent: {intent_result.intent}\n"
            f"User sentiment: {sentiment_profile.sentiment}\n"
            f"Humor preference: {sentiment_profile.humor_level}\n"
        )

        response_chunks: list[str] = []
        async for delta in provider.stream_chat(prompt_with_tools, system_prompt):
            response_chunks.append(delta)
            if emit:
                await emit(
                    make_event(
                        SocketEventType.ASSISTANT_DELTA,
                        session_id=session_id,
                        delta=delta,
                    ).model_dump(mode="json")
                )

        response_text = "".join(response_chunks).strip()
        if not response_text:
            response_text = await provider.complete_chat(prompt_with_tools, system_prompt)

        assistant_message = ChatMessage(role=ChatRole.ASSISTANT, content=response_text)
        await self.conversation_repository.append_message(
            session_id=session_id,
            role=ChatRole.ASSISTANT.value,
            content=response_text,
            metadata={"provider": provider_type.value},
        )
        await self.memory_repository.store_fact(
            session_id=session_id,
            content=f"User asked: {request.prompt}\nAssistant answered: {response_text[:300]}",
        )

        if emit:
            await emit(
                make_event(
                    SocketEventType.ASSISTANT_DONE,
                    session_id=session_id,
                    message=response_text,
                    structured_results={
                        "intent": intent_result.model_dump(),
                        "route": route_result.model_dump(),
                        "sentiment": sentiment_profile.model_dump(),
                    },
                    process_entries=agent_process_entries,
                    tool_results=[result.model_dump(mode="json") for result in tool_results],
                ).model_dump(mode="json")
            )

        return ChatResponsePayload(
            session_id=session_id,
            provider=provider_type,
            message=assistant_message,
            tool_results=[result.model_dump() for result in tool_results],
            memory_hits=[memory.content for memory in memories],
            process_entries=process_entries,
            structured_results={
                "intent": intent_result.model_dump(),
                "route": route_result.model_dump(),
                "sentiment": sentiment_profile.model_dump(),
            },
        )

    async def _maybe_run_tools(
        self,
        session_id: str,
        prompt: str,
        provider: BaseLLMProvider,
        emit: EmitFn | None,
    ):
        plan = await self.agent_planner.create_plan(prompt, provider)
        plan_entries = self._plan_entries(plan)
        results = []
        for step in plan.steps:
            try:
                self.tool_registry.get(step.tool_name)
            except KeyError:
                continue
            if emit:
                await emit(
                    make_event(
                        SocketEventType.TOOL_STARTED,
                        session_id=session_id,
                        tool_name=step.tool_name,
                    ).model_dump(mode="json")
                )
            result = await self.tool_registry.execute(session_id=session_id, tool_name=step.tool_name, args=step.args)
            results.append(result)
            await self.trace_repository.record(session_id, result.model_dump(mode="json"))
            if emit:
                await emit(
                    make_event(
                        SocketEventType.TOOL_OUTPUT,
                        session_id=session_id,
                        tool_name=step.tool_name,
                        output=result.output,
                    ).model_dump(mode="json")
                )
                await emit(
                    make_event(
                        SocketEventType.TOOL_DONE,
                        session_id=session_id,
                        tool_name=step.tool_name,
                        success=result.success,
                    ).model_dump(mode="json")
                )
        return results, plan_entries

    def _plan_entries(self, plan) -> list[dict[str, str]]:
        if not plan.steps:
            return []
        entries = [
            {
                "type": "agent.plan",
                "label": "tool plan",
                "detail": plan.rationale or f"{plan.source} planner selected {len(plan.steps)} step(s).",
            }
        ]
        entries.extend(
            {
                "type": "agent.step",
                "label": step.tool_name,
                "detail": step.reason,
            }
            for step in plan.steps
        )
        return entries

    def _format_tool_result(self, result) -> str:
        status = "success" if result.success else "failure"
        return f"[{result.tool_name} | {status}]\n{result.output}"
