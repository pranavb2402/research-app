import asyncio
from datetime import datetime, timezone
from config.database import session
from controller.research.background_research import search_web, search_documentation, search_knowledge_base
from schemas.question import Question, QuestionStatus
from schemas.research_job import ResearchJob
import models.question
import models.research_job
from controller.llm.answer import get_answer_from_llm
from schemas.answer import Answer



async def get_all_research_done(question : Question) -> ResearchJob | None:
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
        # each source gets its own 5s limit; a slow or failing one is skipped, the rest still count
        result = await asyncio.gather(
            asyncio.wait_for(search_web(question=question.question), 5),
            asyncio.wait_for(search_documentation(question=question.question), 5),
            asyncio.wait_for(search_knowledge_base(question=question.question), 5),
            return_exceptions=True,
        )
        result = [r for r in result if not isinstance(r, BaseException)]

        if not result:
            try:
                db.query(models.question.Question).filter(models.question.Question.id == question.id).update(
                    {models.question.Question.status: QuestionStatus.FAILED}
                )
                db.commit()
            except Exception:
                db.rollback()
                raise
            return None

        try:
            answer_from_llm = await asyncio.wait_for(get_answer_from_llm(question.question, result), 6)
        except Exception:
            try:
                db.query(models.question.Question).filter(models.question.Question.id == question.id).update(
                    {models.question.Question.status: QuestionStatus.FAILED}
                )
                db.commit()
            except Exception:
                db.rollback()
                raise
            return None

        research_job = ResearchJob(
            id=question.id,
            question=question.question,
            summary=answer_from_llm.summary,
            confidence=answer_from_llm.confidance,
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
