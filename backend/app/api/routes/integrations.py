import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.workspace import HomeAssistantResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])
logger = logging.getLogger(__name__)


@router.get("/home-assistant/status", response_model=HomeAssistantResponse)
async def home_assistant_status(request: Request) -> HomeAssistantResponse | JSONResponse:
    try:
        result = await request.app.state.container.workspace_service.home_status()
        return HomeAssistantResponse(data=result)
    except Exception:
        logger.exception("Error fetching Home Assistant status")
        return JSONResponse(status_code=500, content={"detail": "Internal error fetching Home Assistant status"})
