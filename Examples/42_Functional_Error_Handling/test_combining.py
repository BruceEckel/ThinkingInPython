# test_combining.py
import pytest
from combining import combined
from result import Err, Ok, Result

@pytest.mark.parametrize("a, b, expected", [
    (7, 5, Ok("add(7 + 5 + 12): 24")),
    (1, 5, Err("func_a(1)")),
    (2, 1, Err("func_c(3): division by zero")),
])
def test_combined(
    a: int, b: int, expected: Result[str, str]
) -> None:
    assert combined(a, b) == expected
