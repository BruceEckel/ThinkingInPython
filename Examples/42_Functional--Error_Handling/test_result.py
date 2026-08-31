# test_result.py
from result import Err, Ok

def test_success_unwrap() -> None:
    assert Ok(5).unwrap() == 5

def test_bind_chains_a_success() -> None:
    assert Ok(1).bind(lambda x: Ok(x + 1)) == Ok(2)

def test_bind_short_circuits_a_failure() -> None:
    failure: Err[str] = Err("boom")
    assert failure.bind(lambda x: Ok(x + 1)) is failure
