# test_repeat.py
import pytest
from repeat import repeat

@pytest.mark.parametrize("times, expected", [
    (3, 3),
    (1, 1),
])
def test_repeat_call_count(times: int, expected: int) -> None:
    calls: list[str] = []

    @repeat(times=times)
    def record() -> None:
        calls.append("call")

    record()
    assert len(calls) == expected

@pytest.mark.parametrize("times", [0, -1])
def test_repeat_rejects_times_below_one(times: int) -> None:
    with pytest.raises(ValueError):
        repeat(times=times)
