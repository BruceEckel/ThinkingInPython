# test_result_announce.py
from exercise_5 import Broadcaster, succeeds
from result import Err, Result

def test_later_listener_runs_after_an_err() -> None:
    received: list[int] = []

    def broken(data: int) -> Result[None, str]:
        return Err("boom")

    source = Broadcaster[int]()
    source.subscribe(broken)
    source.subscribe(succeeds(received.append))
    assert source.announce(1) == [Err("boom")]
    assert received == [1]
