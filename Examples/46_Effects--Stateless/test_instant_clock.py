# test_instant_clock.py
import time
from dataclasses import field
from typing import override
from record import record
from sleep_effect import delayed_sum
from stateless import as_type, run, supply
from stateless.time import Time

@record(slots=False)
class Instant(Time):
    waited: list[float] = field(default_factory=list)
    @override
    async def sleep(self, seconds: float) -> None:
        self.waited.append(seconds)

def test_delayed_sum() -> None:
    clock = Instant()
    start = time.perf_counter()
    supplied = supply(as_type(Time)(clock))
    assert run(supplied(delayed_sum)([1, 2, 3])) == 6
    assert clock.waited == [0.01, 0.01, 0.01]
    assert time.perf_counter() - start < 0.5
