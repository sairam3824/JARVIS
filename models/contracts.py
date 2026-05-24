from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field

from models.chat import ChatMessage, ProviderType


class ToolSafetyLevel(str, Enum):
    SAFE = "safe"
    CONFIRM = "confirm"
    RESTRICTED = "restricted"


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    safety_level: ToolSafetyLevel = ToolSafetyLevel.SAFE
    requires_confirmation: bool = False
    category: str = "general"
    capability_tags: list[str] = Field(default_factory=list)
    result_type: str = "text"


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    output: str
    structured_output: dict[str, Any] = Field(default_factory=dict)
    result_type: str = "text"
    category: str = "general"


class MemoryRecord(BaseModel):
    kind: str
    content: str
    relevance: float = 0.0


class SystemSnapshot(BaseModel):
    cpu_percent: float
    memory_percent: float
    available_memory_mb: float
    running_tools: list[str] = Field(default_factory=list)
    recent_logs: list[str] = Field(default_factory=list)


class ModelRouteResult(BaseModel):
    provider: ProviderType
    task: str
    model_name: str
    reason: str


class IntentClassification(BaseModel):
    intent: str
    confidence: float
    labels: list[str] = Field(default_factory=list)
    entities: dict[str, Any] = Field(default_factory=dict)


class SentimentHumorProfile(BaseModel):
    sentiment: str
    humor_level: str
    friendliness: float = 0.0
    confidence: float = 0.0


class AudioFeatureProfile(BaseModel):
    duration_seconds: float | None = None
    signal_strength: float = 0.0
    file_size_bytes: int = 0
    descriptors: dict[str, Any] = Field(default_factory=dict)


class TemplateSuggestion(BaseModel):
    title: str
    tone: str
    content: str


class PlannerItem(BaseModel):
    title: str
    notes: str = ""
    time_slot: str | None = None
    completed: bool = False


class PlannerPreview(BaseModel):
    kind: str
    title: str
    summary: str
    items: list[PlannerItem] = Field(default_factory=list)
    templates: list[TemplateSuggestion] = Field(default_factory=list)
    recipe: dict[str, Any] = Field(default_factory=dict)


class AnalyticsSummary(BaseModel):
    dataset_name: str
    row_count: int
    column_count: int
    numeric_columns: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)


class VisionAnalysisResult(BaseModel):
    filename: str
    width: int
    height: int
    dominant_colors: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    summary: str
    similar_assets: list[str] = Field(default_factory=list)


class QRResult(BaseModel):
    mode: str
    payload_text: str | None = None
    decoded_text: str | None = None
    image_base64: str | None = None


class HomeDeviceStatus(BaseModel):
    entity_id: str
    state: str
    area: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class HomeAssistantSummary(BaseModel):
    status: str
    endpoint: str | None = None
    devices: list[HomeDeviceStatus] = Field(default_factory=list)
    alerts: list[str] = Field(default_factory=list)


@dataclass(slots=True)
class ToolContext:
    session_id: str
    allowed_roots: list[Path]
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    definition: ToolDefinition

    @abstractmethod
    async def run(self, context: ToolContext, args: dict[str, Any]) -> ToolExecutionResult:
        raise NotImplementedError


class BaseLLMProvider(ABC):
    provider_type: ProviderType

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[ChatMessage],
        system_prompt: str,
    ) -> AsyncIterator[str]:
        raise NotImplementedError

    @abstractmethod
    async def complete_chat(
        self,
        messages: list[ChatMessage],
        system_prompt: str,
    ) -> str:
        raise NotImplementedError

    async def transcribe_audio(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError("This provider does not support transcription")

    async def synthesize_speech(self, text: str) -> bytes:
        raise NotImplementedError("This provider does not support speech synthesis")


class BaseModelRouter(ABC):
    @abstractmethod
    async def select_route(
        self,
        prompt: str,
        requested_provider: ProviderType | None = None,
    ) -> tuple[IntentClassification, ModelRouteResult]:
        raise NotImplementedError


class BaseTextClassifier(ABC):
    @abstractmethod
    async def classify(self, text: str) -> IntentClassification:
        raise NotImplementedError


class BaseVisionAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, image_bytes: bytes, filename: str) -> VisionAnalysisResult:
        raise NotImplementedError


class BaseAudioFeatureExtractor(ABC):
    @abstractmethod
    async def extract(self, audio_bytes: bytes, filename: str) -> AudioFeatureProfile:
        raise NotImplementedError


class BasePlannerEngine(ABC):
    @abstractmethod
    async def preview(self, kind: str, objective: str, context: dict[str, Any] | None = None) -> PlannerPreview:
        raise NotImplementedError


class BaseSentimentHumorScorer(ABC):
    @abstractmethod
    async def score(self, text: str) -> SentimentHumorProfile:
        raise NotImplementedError


class BaseRecipePlanner(ABC):
    @abstractmethod
    async def generate_recipe(self, prompt: str, pantry: list[str] | None = None) -> PlannerPreview:
        raise NotImplementedError


class BaseDesktopAutomationAdapter(ABC):
    @abstractmethod
    async def open_target(self, target: str, mode: str = "application") -> dict[str, Any]:
        raise NotImplementedError


class BaseHomeAssistantAdapter(ABC):
    @abstractmethod
    async def fetch_status(self) -> HomeAssistantSummary:
        raise NotImplementedError
