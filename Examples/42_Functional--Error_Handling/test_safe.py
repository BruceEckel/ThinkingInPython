# test_safe.py
from result import Err, Ok
from safe_demo import parse

def test_good_input_becomes_an_ok() -> None:
    assert parse("42") == Ok(42)

def test_exception_becomes_an_err() -> None:
    match parse("oops"):
        case Err(error):
            assert isinstance(error, ValueError)
        case _:
            raise AssertionError("expected an Err")
