# test_resilient_notify.py
import pytest
from exercise_3 import Observable

def test_later_observer_still_runs_after_a_failure() -> None:
    received: list[int] = []

    def broken(data: int) -> None:
        raise RuntimeError("boom")

    obs = Observable[int]()
    obs.subscribe(broken)
    obs.subscribe(received.append)
    with pytest.raises(ExceptionGroup):
        obs.notify(1)
    assert received == [1]
