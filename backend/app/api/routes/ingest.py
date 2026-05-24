from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.workspace import DatasetIngestResponse

router = APIRouter(prefix="/ingest", tags=["workspace"])
logger = logging.getLogger(__name__)


@router.post("/data", response_model=DatasetIngestResponse)
async def ingest_data(
    request: Request,
    dataset_name: str = Form(...),
    kind: str = Form(default="csv"),
    content: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> DatasetIngestResponse | JSONResponse:
    try:
        file_bytes = await file.read() if file else None
        result = await request.app.state.container.workspace_service.ingest_dataset(
            dataset_name=dataset_name,
            kind=kind,
            content=content,
            file_bytes=file_bytes,
            filename=file.filename if file else None,
        )
        return DatasetIngestResponse(data=result)
    except Exception:
        logger.exception("Error ingesting dataset")
        return JSONResponse(status_code=500, content={"detail": "Internal error ingesting dataset"})
