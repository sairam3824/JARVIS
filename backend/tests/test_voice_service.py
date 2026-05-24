from __future__ import annotations

import pytest

from app.services.voice_service import VoiceService
from models.chat import ChatMessage, ChatResponsePayload, ChatRole, ProviderType
from models.contracts import AudioFeatureProfile


class OrchestratorStub:
    def __init__(self) -> None:
        self.request = None

    async def run_chat(self, request, emit=None):
        self.request = request
        return ChatResponsePayload(
            session_id="voice-session",
            provider=ProviderType.OPENROUTER,
            message=ChatMessage(role=ChatRole.ASSISTANT, content="Voice reply"),
        )


class SpeechProviderStub:
    async def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        return "Recorded transcript"

    async def synthesize_speech(self, text: str) -> bytes:
        return b"audio-bytes"


class AudioFeatureExtractorStub:
    async def extract(self, audio_bytes: bytes, filename: str) -> AudioFeatureProfile:
        return AudioFeatureProfile(signal_strength=0.42, file_size_bytes=len(audio_bytes))


@pytest.mark.asyncio
async def test_voice_service_defaults_to_openrouter_provider():
    orchestrator = OrchestratorStub()
    service = VoiceService(
        orchestrator=orchestrator,
        speech_provider=SpeechProviderStub(),
        audio_feature_extractor=AudioFeatureExtractorStub(),
    )

    response = await service.handle_voice(
        audio_bytes=b"voice-bytes",
        filename="recording.webm",
        provider=None,
        session_id=None,
    )

    assert orchestrator.request.provider == ProviderType.OPENROUTER
    assert response.provider == ProviderType.OPENROUTER
    assert response.audio_base64 is not None
