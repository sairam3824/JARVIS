from __future__ import annotations

import base64

from models.chat import ProviderType, VoiceResponsePayload


class VoiceService:
    def __init__(self, orchestrator, speech_provider, audio_feature_extractor) -> None:
        self.orchestrator = orchestrator
        self.speech_provider = speech_provider
        self.audio_feature_extractor = audio_feature_extractor

    async def handle_voice(self, audio_bytes: bytes, filename: str, provider: str | None, session_id: str | None):
        transcript = await self.speech_provider.transcribe_audio(audio_bytes, filename)
        audio_features = await self.audio_feature_extractor.extract(audio_bytes, filename)
        chat_result = await self.orchestrator.run_chat(
            request=self._build_request(transcript, provider, session_id),
            emit=None,
        )
        try:
            speech = await self.speech_provider.synthesize_speech(chat_result.message.content)
        except Exception:
            speech = b""
        encoded_audio = base64.b64encode(speech).decode("utf-8") if speech else None
        return VoiceResponsePayload(
            session_id=chat_result.session_id,
            transcript=transcript,
            provider=chat_result.provider,
            response_text=chat_result.message.content,
            audio_base64=encoded_audio,
            tool_results=chat_result.tool_results,
            process_entries=[
                *chat_result.process_entries,
                {
                    "type": "audio.features",
                    "label": filename,
                    "detail": f"signal={audio_features.signal_strength:.2f}",
                },
            ],
            structured_results={
                **chat_result.structured_results,
                "audio_features": audio_features.model_dump(),
            },
        )

    def _build_request(self, transcript: str, provider: str | None, session_id: str | None):
        from models.chat import ChatRequestPayload

        resolved = ProviderType.OPENROUTER
        if provider:
            try:
                resolved = ProviderType(provider)
            except ValueError:
                pass

        return ChatRequestPayload(
            prompt=transcript,
            provider=resolved,
            session_id=session_id,
            voice_mode=True,
        )
