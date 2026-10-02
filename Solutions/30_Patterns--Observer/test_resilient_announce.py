# test_resilient_announce.py
import pytest
from exercise_3 import Broadcaster

def test_later_responder_still_runs_after_a_failure(
) -> None:
    received: list[int] = []

    def broken(data: int) -> None:
        raise RuntimeError("boom")

    broadcaster = Broadcaster[int]()
    broadcaster.connect(broken)
    broadcaster.connect(received.append)
    with pytest.raises(ExceptionGroup):
        broadcaster.announce(1)
    assert received == [1]
