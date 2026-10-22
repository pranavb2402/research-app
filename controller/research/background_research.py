import asyncio


async def search_web(question) -> str:
    await asyncio.sleep(4)
    return "Here is the dog from web"

async def search_documentation(question):
    await asyncio.sleep(7)
    return "Here is the dog from doc"

async def search_knowledge_base(question):
    await asyncio.sleep(4)
    return "Here is the dog from kb"
