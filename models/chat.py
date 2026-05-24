from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProviderType(str, Enum):
    OPENROUTER = "openrouter"


class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    role: ChatRole
    content: str
    created_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequestPayload(BaseModel):
    prompt: str
    provider: ProviderType | None = None
    session_id: str | None = None
    voice_mode: bool = False


class ChatResponsePayload(BaseModel):
    session_id: str
    provider: ProviderType
    message: ChatMessage
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    memory_hits: list[str] = Field(default_factory=list)
    process_entries: list[dict[str, Any]] = Field(default_factory=list)
    structured_results: dict[str, Any] = Field(default_factory=dict)


class VoiceResponsePayload(BaseModel):
    session_id: str
    transcript: str
    provider: ProviderType
    response_text: str
    audio_base64: str | None = None
    mime_type: str = "audio/mpeg"
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    process_entries: list[dict[str, Any]] = Field(default_factory=list)
    structured_results: dict[str, Any] = Field(default_factory=dict)
