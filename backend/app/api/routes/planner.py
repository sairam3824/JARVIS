import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.workspace import PlannerPreviewRequest, PlannerPreviewResponse

router = APIRouter(prefix="/planner", tags=["planner"])
logger = logging.getLogger(__name__)


@router.post("/preview", response_model=PlannerPreviewResponse)
async def planner_preview(request: Request, payload: PlannerPreviewRequest) -> PlannerPreviewResponse | JSONResponse:
    try:
        result = await request.app.state.container.workspace_service.preview_plan(
            session_id=payload.session_id,
            kind=payload.kind,
            objective=payload.objective,
            context=payload.context,
        )
        return PlannerPreviewResponse(data=result)
    except Exception:
        logger.exception("Error generating planner preview")
        return JSONResponse(status_code=500, content={"detail": "Internal error generating planner preview"})
