from pydantic import BaseModel

from models.chat import VoiceResponsePayload


class VoiceResponse(BaseModel):
    data: VoiceResponsePayload

