from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from models.events import SocketEventType, make_event

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/system")
async def system_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            try:
                snapshot = await websocket.app.state.container.system_service.snapshot()
                event = make_event(SocketEventType.SYSTEM_SNAPSHOT, **snapshot.model_dump())
                await websocket.send_json(event.model_dump(mode="json"))
            except WebSocketDisconnect:
                return
            except Exception:
                logger.exception("Error in system snapshot")
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        return

