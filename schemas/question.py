from pydantic import BaseModel
from uuid import UUID
from enum import StrEnum

class QuestionStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED="completed"

class Question(BaseModel):
    id: UUID
    question: str
    status: QuestionStatus = QuestionStatus.PENDING
