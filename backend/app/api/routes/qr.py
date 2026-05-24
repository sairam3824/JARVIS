from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.workspace import QRResponse

router = APIRouter(prefix="/qr", tags=["qr"])
logger = logging.getLogger(__name__)


@router.post("", response_model=QRResponse)
async def qr_flow(
    request: Request,
    mode: str = Form(...),
    payload_text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> QRResponse | JSONResponse:
    try:
        if mode == "scan" and file is not None:
            image_bytes = await file.read()
            result = await request.app.state.container.workspace_service.handle_qr_scan(image_bytes)
        else:
            result = await request.app.state.container.workspace_service.handle_qr_generate(payload_text or "")
        return QRResponse(data=result)
    except Exception:
        logger.exception("Error processing QR request")
        return JSONResponse(status_code=500, content={"detail": "Internal error processing QR request"})
