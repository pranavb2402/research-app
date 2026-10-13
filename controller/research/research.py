import asyncio
from datetime import datetime, timezone
from config.database import session
from controller.research.background_research import search_web, search_documentation, search_knowledge_base
from schemas.question import Question, QuestionStatus
from schemas.research_job import ResearchJob
import models.question
import models.research_job


async def get_all_research_done(question : Question) -> ResearchJob:
    # runs as a background task after the response is sent, so it needs its own session
    db = session()
    try:
        created_at = datetime.now(timezone.utc)
        try:
            db.query(models.question.Question).filter(models.question.Question.id == question.id).update(
                {models.question.Question.status: QuestionStatus.IN_PROGRESS}
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        result = await asyncio.gather(
    search_web(question=question.question),
    search_documentation(question=question.question),
    search_knowledge_base(question=question.question)
        )

        research_job = ResearchJob(
            id=question.id,
            question=question.question,
            summary="\n".join(result),
            confidence=0.85,
            created_at=created_at,
            completed_at=datetime.now(timezone.utc),
        )
        try:
            db.add(models.research_job.ResearchJob(**research_job.model_dump()))
            db.query(models.question.Question).filter(models.question.Question.id == question.id).update(
                        {models.question.Question.status: QuestionStatus.COMPLETED}
                    )
            db.commit()
        except Exception:
            db.rollback()
            raise

        return research_job
    finally:
        db.close()
