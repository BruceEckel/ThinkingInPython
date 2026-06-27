# test_combining.py
from combining import combined
from result import Failure, Success

def test_combined() -> None:
    assert combined(7, 5) == Success("add(7 + 5 + 12): 24")
    assert combined(1, 5) == Failure("func_a(1)")
    assert combined(2, 1) == Failure("func_c(3): division by zero")
