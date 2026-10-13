from fastapi import FastAPI,Depends
from pydantic import BaseModel
from config.database import session,engine
from sqlalchemy.orm import Session
import models.question
import models.research_job
from uuid import uuid4
from dependencies.database import get_db
from router.research import research

app  = FastAPI()
models.question.Base.metadata.create_all(bind=engine)

def init_db():
    db = session()

    db.commit()
    db.close()

init_db()


@app.get("/test")
def start():
    return {"Server is running"}

app.include_router(research)
