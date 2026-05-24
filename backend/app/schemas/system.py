from pydantic import BaseModel

from models.contracts import SystemSnapshot


class SystemResponse(BaseModel):
    data: SystemSnapshot

