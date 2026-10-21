from pydantic import BaseModel

class Answer(BaseModel):
    summary: str
    confidance: float