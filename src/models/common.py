from pydantic import BaseModel


class IdResponse(BaseModel):
    id: str


class MessageResponse(BaseModel):
    message: str
