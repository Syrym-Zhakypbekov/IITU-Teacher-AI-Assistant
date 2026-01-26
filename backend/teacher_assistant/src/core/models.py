from pydantic import BaseModel
from typing import List, Optional

class TutorRecord(BaseModel):
    tutor: str
    topic: str
    content: str
    vector: Optional[List[float]] = None

class RAGResponse(BaseModel):
    query: str
    response: str
    references: List[str]
    confidence_score: float
