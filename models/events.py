from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SocketEventType(str, Enum):
    SESSION_STARTED = "session.started"
    INTENT_DETECTED = "intent.detected"
    MODEL_SELECTED = "model.selected"
    PLANNER_UPDATED = "planner.updated"
    ANALYTICS_READY = "analytics.ready"
    VISION_READY = "vision.ready"
    INTEGRATION_STATUS = "integration.status"
    ASSISTANT_DELTA = "assistant.delta"
    ASSISTANT_DONE = "assistant.done"
    TOOL_STARTED = "tool.started"
    TOOL_OUTPUT = "tool.output"
    TOOL_DONE = "tool.done"
    ERROR = "error"
    SYSTEM_SNAPSHOT = "system.snapshot"


class SocketEvent(BaseModel):
    type: SocketEventType
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)


def make_event(event_type: SocketEventType, **payload: Any) -> SocketEvent:
    return SocketEvent(type=event_type, payload=payload)
