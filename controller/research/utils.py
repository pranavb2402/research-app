import asyncio

async def exponential_retry(callback: function, retry: int = 1, max_retry: int = 3, timeout: int = 5):
    try:
        result = await asyncio.wait_for(callback(), timeout + retry - 1)
        return result
    except Exception as e :
        if (retry == max_retry):
            raise Exception(e)
        return await exponential_retry(callback=callback, retry=retry+1, max_retry=max_retry, timeout=timeout)
