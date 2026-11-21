from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    conversation_id: int | None = None
    content: str = Field(min_length=1, max_length=5000)