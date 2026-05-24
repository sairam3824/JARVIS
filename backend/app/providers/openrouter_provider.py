from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from typing import AsyncIterator

import httpx

from app.core.config import Settings
from models.chat import ChatMessage, ProviderType
from models.contracts import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    provider_type = ProviderType.OPENROUTER

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def stream_chat(self, messages: list[ChatMessage], system_prompt: str) -> AsyncIterator[str]:
        text = await self.complete_chat(messages, system_prompt)
        for index in range(0, len(text), 32):
            await asyncio.sleep(0.01)
            yield text[index:index + 32]

    async def complete_chat(self, messages: list[ChatMessage], system_prompt: str) -> str:
        if not self.settings.openrouter_api_key:
            return "OpenRouter is not configured yet."
        payload = self._build_chat_payload(messages, system_prompt)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            return f"OpenRouter API error: {exc.response.status_code}"
        except httpx.RequestError as exc:
            return f"OpenRouter connection error: {exc}"
        return self._extract_message_text(data)

    async def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        if not self.settings.openrouter_api_key:
            return "Voice mode requires OPENROUTER_API_KEY."
        payload = {
            "model": self.settings.openrouter_audio_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Transcribe this audio verbatim. Return only the spoken transcript text.",
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": base64.b64encode(audio_bytes).decode("utf-8"),
                                "format": self._audio_format(filename),
                            },
                        },
                    ],
                }
            ],
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            return f"Transcription API error: {exc.response.status_code}"
        except httpx.RequestError as exc:
            return f"Transcription connection error: {exc}"
        return self._extract_message_text(data)

    async def synthesize_speech(self, text: str) -> bytes:
        if not self.settings.openrouter_api_key:
            return b""
        payload = {
            "model": self.settings.openrouter_audio_model,
            "modalities": ["audio"],
            "audio": {
                "voice": self.settings.tts_voice,
                "format": "mp3",
            },
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": text}],
                }
            ],
            "stream": True,
        }
        audio_chunks: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    self.base_url,
                    headers=self._headers(),
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        chunk = line.removeprefix("data:").strip()
                        if not chunk or chunk == "[DONE]":
                            continue
                        try:
                            event = json.loads(chunk)
                        except json.JSONDecodeError:
                            continue
                        audio_delta = event.get("choices", [{}])[0].get("delta", {}).get("audio", {})
                        if audio_delta.get("data"):
                            audio_chunks.append(audio_delta["data"])
        except (httpx.HTTPStatusError, httpx.RequestError):
            return b""
        if not audio_chunks:
            return b""
        return base64.b64decode("".join(audio_chunks))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }

    def _build_chat_payload(self, messages: list[ChatMessage], system_prompt: str) -> dict[str, object]:
        tool_context = self._tool_context(messages)
        serialized_messages = [{"role": "system", "content": self._merge_system_prompt(system_prompt, tool_context)}]
        serialized_messages.extend(
            {"role": message.role.value, "content": message.content}
            for message in messages
            if message.role.value != "tool"
        )
        return {
            "model": self.settings.openrouter_model,
            "messages": serialized_messages,
        }

    def _extract_message_text(self, data: dict) -> str:
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_segments = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_segments.append(block.get("text", ""))
            return "".join(text_segments)
        return ""

    def _audio_format(self, filename: str) -> str:
        suffix = Path(filename).suffix.lower().lstrip(".")
        return suffix or "webm"

    def _tool_context(self, messages: list[ChatMessage]) -> str:
        tool_messages = [message.content for message in messages if message.role.value == "tool"]
        if not tool_messages:
            return ""

        observations = []
        for index, content in enumerate(tool_messages, start=1):
            observations.append(f"Observation {index}:\n{content}")
        return "Tool observations gathered before answering:\n" + "\n\n".join(observations)

    def _merge_system_prompt(self, system_prompt: str, tool_context: str) -> str:
        if not tool_context:
            return system_prompt
        return f"{system_prompt}\n\n{tool_context}"
