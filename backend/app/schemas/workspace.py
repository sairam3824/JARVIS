from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from models.contracts import HomeAssistantSummary, PlannerPreview, QRResult, VisionAnalysisResult
from models.workspace import DatasetIngestResult


class PlannerPreviewRequest(BaseModel):
    kind: str = Field(default="checklist")
    objective: str
    session_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class PlannerPreviewResponse(BaseModel):
    data: PlannerPreview


class DatasetIngestResponse(BaseModel):
    data: DatasetIngestResult


class VisionAnalysisResponse(BaseModel):
    data: VisionAnalysisResult


class QRResponse(BaseModel):
    data: QRResult


class HomeAssistantResponse(BaseModel):
    data: HomeAssistantSummary

