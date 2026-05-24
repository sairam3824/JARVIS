import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse | JSONResponse:
    try:
        result = await request.app.state.container.chat_service.handle_chat(
            prompt=payload.prompt,
            provider=payload.provider,
            session_id=payload.session_id,
            voice_mode=payload.voice_mode,
        )
        return ChatResponse(data=result)
    except Exception:
        logger.exception("Error handling chat request")
        return JSONResponse(status_code=500, content={"detail": "Internal error processing chat request"})
