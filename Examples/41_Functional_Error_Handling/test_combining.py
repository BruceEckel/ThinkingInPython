# test_combining.py
import pytest
from combining import combined
from result import Failure, Result, Success

@pytest.mark.parametrize("a, b, expected", [
    (7, 5, Success("add(7 + 5 + 12): 24")),
    (1, 5, Failure("func_a(1)")),
    (2, 1, Failure("func_c(3): division by zero")),
])
def test_combined(
    a: int, b: int, expected: Result[str, str]
) -> None:
    assert combined(a, b) == expected
