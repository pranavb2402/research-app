from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel
from config.database import session,engine
from sqlalchemy.orm import Session
import models.question
from schemas.question import Question,QuestionStatus
from uuid import uuid4

app  = FastAPI()
models.question.Base.metadata.create_all(bind=engine)


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()

    db.commit()
    db.close()

init_db()


@app.get("/test")
def start():
    return {"Server is running"}

@app.post("/research")
def post_questions(q: str, db: Session = Depends(get_db)):
    question: Question = Question(id=uuid4(), question=q)
    try:
        db.add(models.question.Question(**question.model_dump()))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return question
