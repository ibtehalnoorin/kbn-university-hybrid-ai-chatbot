from typing import Optional
from pydantic import BaseModel, Field

class AddKnowledgeSourceRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=512, description="Website URL to ingest")
    name: Optional[str] = Field(None, max_length=255, description="Display name for the source")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the source")
