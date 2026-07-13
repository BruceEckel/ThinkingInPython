# test_repeat_class.py
import pytest
from repeat_class import repeat

@pytest.mark.parametrize("times, expected", [
    (3, 3),
    (1, 1),
    (0, 1),
    (-1, 1),
])
def test_repeat_call_count(times: int, expected: int) -> None:
    calls: list[str] = []

    @repeat(times=times)
    def record() -> None:
        calls.append("call")

    record()
    assert len(calls) == expected
