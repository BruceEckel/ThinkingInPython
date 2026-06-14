# FunctionalErrorHandling/test_result.py
from combining import combined
from composing import composed as composed_manual
from composing_with_bind import composed as composed_bind
from result import Failure, Success


def test_success_unwrap() -> None:
    assert Success(5).unwrap() == 5


def test_bind_chains_a_success() -> None:
    assert Success(1).bind(lambda x: Success(x + 1)) == Success(2)


def test_bind_short_circuits_a_failure() -> None:
    failure: Failure[str] = Failure("boom")
    assert failure.bind(lambda x: Success(x + 1)) is failure


def test_manual_and_bind_agree() -> None:
    for i in range(5):
        assert composed_manual(i) == composed_bind(i)


def test_combined() -> None:
    assert combined(7, 5) == Success("add(7 + 5 + 12): 24")
    assert combined(1, 5) == Failure("func_a(1)")
    assert combined(2, 1) == Failure("func_c(3): division by zero")
