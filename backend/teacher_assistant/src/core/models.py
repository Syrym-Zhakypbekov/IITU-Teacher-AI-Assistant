from pydantic import BaseModel
from typing import List, Optional

class KnowledgeChunk(BaseModel):
    content: str
    source: str
    location: str
    vector: Optional[List[float]] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    references: List[str]
    status: str = "success"
