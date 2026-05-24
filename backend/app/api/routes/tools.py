from fastapi import APIRouter, Request

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("")
async def tools(request: Request) -> dict:
    definitions = request.app.state.container.tool_registry.definitions()
    return {"data": [definition.model_dump() for definition in definitions]}

