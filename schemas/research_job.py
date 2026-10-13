from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from schemas.question import QuestionStatus


class ResearchJob(BaseModel):
    id: UUID
    question: str
    summary: str
    confidence: float | None = None
    created_at: datetime
    completed_at: datetime
