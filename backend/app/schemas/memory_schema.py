from typing import Optional
from pydantic import BaseModel, Field

class MemoryCreateRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=128, description="Memory label/key")
    value: str = Field(..., min_length=1, max_length=2000, description="Memory content")
    category: Optional[str] = Field("preference", max_length=64)

class MemoryUpdateRequest(BaseModel):
    key: Optional[str] = Field(None, min_length=1, max_length=128)
    value: Optional[str] = Field(None, min_length=1, max_length=2000)
    category: Optional[str] = Field(None, max_length=64)

class MemoryToggleRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable long-term memory")
