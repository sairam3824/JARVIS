from __future__ import annotations

from functools import cached_property
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="anthropic/claude-sonnet-4.6", alias="OPENROUTER_MODEL")
    openrouter_audio_model: str = Field(default="openai/gpt-audio-mini", alias="OPENROUTER_AUDIO_MODEL")
    tts_voice: str = Field(default="alloy", alias="TTS_VOICE")
    database_url: str = Field(default="sqlite:///backend/data/jarvis.db", alias="DATABASE_URL")
    jarvis_allowed_roots: str = Field(default=".", alias="JARVIS_ALLOWED_ROOTS")
    terminal_timeout_seconds: int = Field(default=15, alias="TERMINAL_TIMEOUT_SECONDS")
    cors_origin: str = Field(default="http://localhost:5173", alias="CORS_ORIGIN")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    home_assistant_url: str | None = Field(default=None, alias="HOME_ASSISTANT_URL")
    home_assistant_token: str | None = Field(default=None, alias="HOME_ASSISTANT_TOKEN")

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), case_sensitive=False, extra="ignore")

    @cached_property
    def database_path(self) -> Path:
        project_root = Path(__file__).resolve().parents[3]
        if self.database_url.startswith("sqlite:///"):
            return (project_root / self.database_url.replace("sqlite:///", "", 1)).resolve()
        return (project_root / self.database_url).resolve()

    @cached_property
    def allowed_roots(self) -> list[str]:
        project_root = Path(__file__).resolve().parents[3]
        return [
            str((project_root / item.strip()).resolve()) if not item.strip().startswith("/") else item.strip()
            for item in self.jarvis_allowed_roots.split(",")
            if item.strip()
        ]


def get_settings() -> Settings:
    return Settings()
