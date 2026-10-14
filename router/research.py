from fastapi import APIRouter,Depends,HTTPException,BackgroundTasks
from schemas.question import Question,QuestionStatus
from schemas.research_job import ResearchJob
from uuid import uuid4, UUID
from sqlalchemy.orm import Session
import models.question
import models.research_job
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

@research.get("/research/{id}")
def get_research_info(id: UUID, db: Session = Depends(get_db)):
    # left join: the job row only exists once the background research has finished
    row = (
        db.query(models.question.Question, models.research_job.ResearchJob)
        .outerjoin(models.research_job.ResearchJob, models.research_job.ResearchJob.id == models.question.Question.id)
        .filter(models.question.Question.id == id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Question not found")
    question, question_research_data = row

    return {
        "id": question.id,
        "status": question.status,
        "summary": question_research_data.summary if question_research_data else None,
        "confidance": question_research_data.confidence if question_research_data else None
    }


@research.get("/research")
def get_all_research_paginated(page: int, limit: int, db:Session = Depends(get_db)):
    offset_val = (page - 1) * limit
    rows = (
        db.query(models.question.Question, models.research_job.ResearchJob)
        .outerjoin(models.research_job.ResearchJob, models.research_job.ResearchJob.id == models.question.Question.id)
        .order_by(models.research_job.ResearchJob.created_at)
        .offset(offset_val)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": question.id,
            "question": question.question,
            "status": question.status,
            "summary": job.summary if job else None,
            "confidance": job.confidence if job else None
        }
        for question, job in rows
    ]

