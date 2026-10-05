# test_combining.py
import pytest
from combining import combined
from result import Err, Ok, Result

@pytest.mark.parametrize("i, j, expected", [
    (7, 5, Ok("add(7 + 5 + 12): 24")),
    (1, 5, Err("func_a(1)")),
    (7, 2, Err("func_b(2)")),
    (2, 1, Err("func_c(3): division by zero")),
    (1, 2, Err("func_a(1)")),
])
def test_combined_returns_answer_or_first_failure(
    i: int, j: int, expected: Result[str, str]
) -> None:
    assert combined(i, j) == expected
