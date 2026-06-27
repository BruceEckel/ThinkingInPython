# test_result.py
from result import Failure, Success

def test_success_unwrap() -> None:
    assert Success(5).unwrap() == 5

def test_bind_chains_a_success() -> None:
    assert Success(1).bind(lambda x: Success(x + 1)) == Success(2)

def test_bind_short_circuits_a_failure() -> None:
    failure: Failure[str] = Failure("boom")
    assert failure.bind(lambda x: Success(x + 1)) is failure
