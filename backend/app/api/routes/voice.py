import logging

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from app.schemas.voice import VoiceResponse

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)


@router.post("", response_model=VoiceResponse)
async def voice(
    request: Request,
    file: UploadFile = File(...),
    provider: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
) -> VoiceResponse | JSONResponse:
    try:
        audio_bytes = await file.read()
        result = await request.app.state.container.voice_service.handle_voice(
            audio_bytes=audio_bytes,
            filename=file.filename or "recording.webm",
            provider=provider,
            session_id=session_id,
        )
        return VoiceResponse(data=result)
    except Exception:
        logger.exception("Error handling voice request")
        return JSONResponse(status_code=500, content={"detail": "Internal error processing voice request"})
