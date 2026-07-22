# async_queue.py
import asyncio

async def consumer(queue: asyncio.Queue[str]) -> None:
    item = await queue.get()  # Suspends until an item arrives
    print(f"consumed {item}")

async def producer(queue: asyncio.Queue[str]) -> None:
    await asyncio.sleep(0.01)  # Stand-in for slow work
    await queue.put("data")

async def main() -> None:
    queue: asyncio.Queue[str] = asyncio.Queue()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(consumer(queue))
        tg.create_task(producer(queue))

asyncio.run(main())
#: consumed data
