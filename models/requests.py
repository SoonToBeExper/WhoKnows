from pydantic import BaseModel

class CreateSessionRequest(BaseModel):
    topic: str
    user_id: str

class SendMessageRequest(BaseModel):
    message: str 