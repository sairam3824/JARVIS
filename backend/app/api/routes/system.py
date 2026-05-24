import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.system import SystemResponse

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)


@router.get("", response_model=SystemResponse)
async def system(request: Request) -> SystemResponse | JSONResponse:
    try:
        result = await request.app.state.container.system_service.snapshot()
        return SystemResponse(data=result)
    except Exception:
        logger.exception("Error fetching system snapshot")
        return JSONResponse(status_code=500, content={"detail": "Internal error fetching system snapshot"})
