from __future__ import annotations

from models.contracts import AnalyticsSummary, HomeAssistantSummary, PlannerPreview, QRResult, VisionAnalysisResult
from models.workspace import DatasetIngestResult


class WorkspaceService:
    def __init__(
        self,
        analytics_service,
        planner_engine,
        recipe_planner,
        vision_analyzer,
        qr_service,
        home_assistant_adapter,
        workspace_repository,
    ) -> None:
        self.analytics_service = analytics_service
        self.planner_engine = planner_engine
        self.recipe_planner = recipe_planner
        self.vision_analyzer = vision_analyzer
        self.qr_service = qr_service
        self.home_assistant_adapter = home_assistant_adapter
        self.workspace_repository = workspace_repository

    async def ingest_dataset(
        self,
        dataset_name: str,
        kind: str,
        content: str | None = None,
        file_bytes: bytes | None = None,
        filename: str | None = None,
    ) -> DatasetIngestResult:
        if file_bytes is not None and filename is not None:
            summary = await self.analytics_service.summarize_file(dataset_name, file_bytes, filename)
            stored_content = file_bytes.decode("utf-8", errors="ignore") if not filename.lower().endswith(".xlsx") else "<binary:xlsx>"
        else:
            summary = await self.analytics_service.summarize_text_dataset(dataset_name, content or "", kind)
            stored_content = content or ""
        dataset_id = await self.workspace_repository.store_dataset(
            name=dataset_name,
            kind=kind,
            content=stored_content,
            metadata={"summary": summary.model_dump()},
        )
        await self.workspace_repository.record_analysis("dataset", dataset_id, "analytics_summary", summary.model_dump())
        return DatasetIngestResult(dataset_id=dataset_id, dataset_name=dataset_name, summary=summary)

    async def analyze_image(self, image_bytes: bytes, filename: str) -> VisionAnalysisResult:
        result = await self.vision_analyzer.analyze(image_bytes, filename)
        await self.workspace_repository.record_analysis("image", None, "vision_analysis", result.model_dump())
        return result

    async def preview_plan(self, session_id: str | None, kind: str, objective: str, context: dict | None = None) -> PlannerPreview:
        if kind == "recipe":
            preview = await self.recipe_planner.generate_recipe(objective, pantry=(context or {}).get("pantry"))
        else:
            preview = await self.planner_engine.preview(kind, objective, context)
        await self.workspace_repository.store_planner_preview(session_id, kind, preview.title, preview.model_dump())
        for template in preview.templates:
            await self.workspace_repository.store_template(kind, template.title, template.content, {"tone": template.tone})
        return preview

    async def handle_qr_generate(self, payload_text: str) -> QRResult:
        result = await self.qr_service.generate(payload_text)
        await self.workspace_repository.store_qr_result(result.mode, result.payload_text, result.decoded_text, result.image_base64)
        return result

    async def handle_qr_scan(self, image_bytes: bytes) -> QRResult:
        result = await self.qr_service.scan(image_bytes)
        await self.workspace_repository.store_qr_result(result.mode, result.payload_text, result.decoded_text, result.image_base64)
        return result

    async def home_status(self) -> HomeAssistantSummary:
        summary = await self.home_assistant_adapter.fetch_status()
        await self.workspace_repository.store_integration_snapshot("home_assistant", summary.model_dump())
        return summary

    async def recent_templates(self) -> list[dict]:
        return await self.workspace_repository.recent_templates()
