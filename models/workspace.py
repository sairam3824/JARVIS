from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from models.contracts import AnalyticsSummary, HomeAssistantSummary, PlannerPreview, QRResult, VisionAnalysisResult


class DatasetIngestResult(BaseModel):
    dataset_id: int
    dataset_name: str
    summary: AnalyticsSummary


class WorkspaceHistoryEntry(BaseModel):
    kind: str
    title: str
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkspaceSnapshot(BaseModel):
    recent_datasets: list[AnalyticsSummary] = Field(default_factory=list)
    recent_plans: list[PlannerPreview] = Field(default_factory=list)
    recent_qr: list[QRResult] = Field(default_factory=list)
    recent_vision: list[VisionAnalysisResult] = Field(default_factory=list)
    home_status: HomeAssistantSummary | None = None
