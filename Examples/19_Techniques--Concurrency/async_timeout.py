# async_timeout.py
import asyncio

async def wait(delay: float) -> str:
    await asyncio.sleep(delay)
    return "done"

async def main() -> None:
    try:
        async with asyncio.timeout(0.05):
            async with asyncio.TaskGroup() as tg:
                fast = tg.create_task(wait(0.01))
                slow = tg.create_task(wait(0.5))
    except TimeoutError:
        print("timed out")
    print(f"fast: {fast.result()}")
    print(f"slow cancelled: {slow.cancelled()}")

asyncio.run(main())
#: timed out
#: fast: done
#: slow cancelled: True
