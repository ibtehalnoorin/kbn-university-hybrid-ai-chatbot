from typing import Optional
from pydantic import BaseModel, Field

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User question or input message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID or None for new")
    stream: Optional[bool] = Field(False, description="Whether to stream response via SSE")

class ConversationUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="New title for the conversation")
