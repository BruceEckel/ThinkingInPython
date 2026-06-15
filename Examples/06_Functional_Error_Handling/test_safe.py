# test_safe.py
from result import Failure, Success
from safe import safe


@safe
def parse(text: str) -> int:
    return int(text)


def test_safe_wraps_a_success() -> None:
    assert parse("42") == Success(42)


def test_safe_captures_the_exception() -> None:
    match parse("oops"):
        case Failure(error):
            assert isinstance(error, ValueError)
        case _:
            raise AssertionError("expected a Failure")
