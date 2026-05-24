from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, ingest, integrations, planner, qr, system, tools, vision, voice
from app.api.ws import chat as chat_ws
from app.api.ws import system as system_ws
from app.core.config import get_settings
from app.core.deps import build_container
from app.core.logging import configure_logging


_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(_settings.log_level)
    container = build_container(_settings)
    container.database.initialize()
    app.state.container = container
    yield


app = FastAPI(title="JARVIS", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[_settings.cors_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(tools.router)
app.include_router(system.router)
app.include_router(ingest.router)
app.include_router(vision.router)
app.include_router(planner.router)
app.include_router(qr.router)
app.include_router(integrations.router)
app.include_router(chat_ws.router)
app.include_router(system_ws.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
