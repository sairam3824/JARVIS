import logging

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.workspace import VisionAnalysisResponse

router = APIRouter(prefix="/vision", tags=["vision"])
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=VisionAnalysisResponse)
async def analyze_image(request: Request, file: UploadFile = File(...)) -> VisionAnalysisResponse | JSONResponse:
    try:
        image_bytes = await file.read()
        result = await request.app.state.container.workspace_service.analyze_image(image_bytes, file.filename or "upload.png")
        return VisionAnalysisResponse(data=result)
    except Exception:
        logger.exception("Error analyzing image")
        return JSONResponse(status_code=500, content={"detail": "Internal error analyzing image"})
