import asyncio
import logging
from datetime import datetime, timezone
from config.database import session
from controller.research.background_research import search_web, search_documentation, search_knowledge_base
from schemas.question import Question, QuestionStatus
from schemas.research_job import ResearchJob
import models.question
import models.research_job
from controller.llm.answer import get_answer_from_llm
from schemas.answer import Answer
from controller.research.utils import exponential_retry

logger = logging.getLogger(__name__)


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
        final_result = await asyncio.gather(
            asyncio.wait_for(search_web(question=question.question), 5),
            asyncio.wait_for(search_documentation(question=question.question), 5),
            asyncio.wait_for(search_knowledge_base(question=question.question), 5),
            return_exceptions=True,
        )

        sources = ["web", "documentation", "knowledge_base"]   # same order as the gather() arguments
        result, errors = [], []

        for source, r in zip(sources, final_result):
            if isinstance(r, TimeoutError):
                logger.warning("%s search timed out", source)
                errors.append(f"{source}: timed out")
            elif isinstance(r, BaseException):
                logger.warning("%s search failed: %r", source, r)
                errors.append(f"{source}: {type(r).__name__}: {r}")
            else:
                result.append(r)

        if not result:
            try:
                db.query(models.question.Question).filter(models.question.Question.id == question.id).update(
                    {models.question.Question.status: QuestionStatus.FAILED, models.question.Question.error_type: "AllSourcesFailed", models.question.Question.error_description: "; ".join(errors)}
                )
                db.commit()
            except Exception:
                db.rollback()
                raise
            return None

        try:
            answer_from_llm = await exponential_retry(lambda: get_answer_from_llm(question.question, result))
        except Exception as e:
            try:
                db.query(models.question.Question).filter(models.question.Question.id == question.id).update(
                    {models.question.Question.status: QuestionStatus.FAILED,models.question.Question.error_type: 'LLM call failed', models.question.Question.error_description: str(e)}
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
