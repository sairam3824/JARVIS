from __future__ import annotations

from models.chat import ChatRequestPayload, ProviderType


def _resolve_provider(provider: str | None) -> ProviderType:
    if provider:
        try:
            return ProviderType(provider)
        except ValueError:
            pass
    return ProviderType.OPENROUTER


class ChatService:
    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator

    async def handle_chat(self, prompt: str, provider: str | None, session_id: str | None, voice_mode: bool = False):
        request = ChatRequestPayload(
            prompt=prompt,
            session_id=session_id,
            provider=_resolve_provider(provider),
            voice_mode=voice_mode,
        )
        return await self.orchestrator.run_chat(request)

    async def stream_chat(self, prompt: str, provider: str | None, session_id: str | None, emit, voice_mode: bool = False):
        request = ChatRequestPayload(
            prompt=prompt,
            session_id=session_id,
            provider=_resolve_provider(provider),
            voice_mode=voice_mode,
        )
        return await self.orchestrator.run_chat(request, emit=emit)
