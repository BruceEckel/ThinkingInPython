# async_timeout.py
import asyncio

async def slow(delay: float) -> str:
    await asyncio.sleep(delay)
    return "done"

async def main() -> None:
    try:
        async with asyncio.timeout(0.05):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(slow(0.01))
                tg.create_task(slow(0.5))
    except TimeoutError:
        print("timed out")

asyncio.run(main())
#: timed out
