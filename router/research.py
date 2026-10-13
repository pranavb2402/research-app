from fastapi import APIRouter,Depends,HTTPException,BackgroundTasks
from schemas.question import Question,QuestionStatus
from uuid import uuid4
from sqlalchemy.orm import Session
import models.question
from dependencies.database import get_db
from controller.research.research import get_all_research_done

research = APIRouter()

@research.post("/research")
def post_questions(q: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    question: Question = Question(id=uuid4(), question=q)
    try:
        db.add(models.question.Question(**question.model_dump()))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    background_tasks.add_task(get_all_research_done, question)
    return question
