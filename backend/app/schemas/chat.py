from pydantic import BaseModel, Field

from models.chat import ChatResponsePayload


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1)
    provider: str | None = None
    session_id: str | None = None
    voice_mode: bool = False


class ChatResponse(BaseModel):
    data: ChatResponsePayload

