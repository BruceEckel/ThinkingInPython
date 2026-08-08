# test_async_resilient_notify.py
import asyncio
import pytest
from exercise_4 import Observable

def test_later_observer_still_runs_after_a_failure() -> None:
    received: list[int] = []

    async def broken(data: int) -> None:
        raise RuntimeError("boom")

    async def record(data: int) -> None:
        await asyncio.sleep(0)
        received.append(data)

    async def run() -> None:
        obs = Observable[int]()
        obs.subscribe(broken)
        obs.subscribe(record)
        with pytest.raises(ExceptionGroup):
            await obs.notify(1)

    asyncio.run(run())
    assert received == [1]
