# test_async_resilient_announce.py
import asyncio
import pytest
from exercise_3 import Broadcaster

def test_later_listener_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    async def broken(data: int) -> None:
        raise RuntimeError("boom")

    async def record(data: int) -> None:
        await asyncio.sleep(0)
        received.append(data)

    async def run() -> None:
        source = Broadcaster[int]()
        source.subscribe(broken)
        source.subscribe(record)
        with pytest.raises(ExceptionGroup):
            await source.announce(1)

    asyncio.run(run())
    assert received == [1]
