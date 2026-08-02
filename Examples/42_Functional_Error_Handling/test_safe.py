# test_safe.py
from result import Err, Ok
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

def test_safe_wraps_a_success() -> None:
    assert parse("42") == Ok(42)

def test_safe_captures_the_exception() -> None:
    match parse("oops"):
        case Err(error):
            assert isinstance(error, ValueError)
        case _:
            raise AssertionError("expected an Err")
