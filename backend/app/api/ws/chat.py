import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/chat")
async def chat_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            prompt = payload.get("prompt")
            if not prompt:
                await websocket.send_json({"type": "error", "payload": {"message": "Missing prompt"}})
                continue

            async def emit(event: dict) -> None:
                await websocket.send_json(event)

            try:
                await websocket.app.state.container.chat_service.stream_chat(
                    prompt=prompt,
                    provider=payload.get("provider"),
                    session_id=payload.get("session_id"),
                    voice_mode=payload.get("voice_mode", False),
                    emit=emit,
                )
            except WebSocketDisconnect:
                return
            except Exception:
                logger.exception("Error during stream_chat")
                await websocket.send_json({"type": "error", "payload": {"message": "Internal error processing request"}})
    except WebSocketDisconnect:
        return

