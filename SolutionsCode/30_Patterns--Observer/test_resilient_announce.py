# test_resilient_announce.py
import pytest
from exercise_3 import Broadcaster

def test_later_listener_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    def broken(data: int) -> None:
        raise RuntimeError("boom")

    source = Broadcaster[int]()
    source.subscribe(broken)
    source.subscribe(received.append)
    with pytest.raises(ExceptionGroup):
        source.announce(1)
    assert received == [1]
