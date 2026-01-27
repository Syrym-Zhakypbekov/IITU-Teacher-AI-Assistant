from pydantic import BaseModel
from typing import List, Optional

class KnowledgeChunk(BaseModel):
    content: str
    source: str
    location: str
    vector: Optional[List[float]] = None

class ChatRequest(BaseModel):
    message: str
    course_id: str
    is_voice: bool = False
    ticket_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    references: List[str]
    status: str = "success"

class CourseCreate(BaseModel):
    id: str
    subject: str
    teacherName: str
    teacherId: str # Links course to a specific teacher
    description: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
