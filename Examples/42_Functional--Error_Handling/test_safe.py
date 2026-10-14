# test_safe.py
from result import Err, Ok
from safe_demo import parse

def test_good_input_becomes_an_ok() -> None:
    assert parse("42") == Ok(42)

def test_exception_becomes_an_err() -> None:
    result = parse("oops")
    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)
