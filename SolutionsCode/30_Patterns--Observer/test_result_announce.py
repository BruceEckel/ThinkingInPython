# test_result_announce.py
from exercise_5 import Broadcaster, succeeds
from result import Err, Result

def test_later_responder_runs_after_an_err() -> None:
    received: list[int] = []

    def broken(data: int) -> Result[None, str]:
        return Err("boom")

    broadcaster = Broadcaster[int]()
    broadcaster.subscribe(broken)
    broadcaster.subscribe(succeeds(received.append))
    assert broadcaster.announce(1) == [Err("boom")]
    assert received == [1]
