import asyncio
from schemas.answer import Answer

async def get_answer_from_llm(q: str, context: list[str]) -> Answer:
    await asyncio.sleep(5)
    llm_answer = Answer(summary="\n".join(context), confidance=0.85)
    return llm_answer