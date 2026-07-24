# test_newtype_boundary.py
from newtype_boundary import UserId

def test_newtype_has_no_runtime_effect() -> None:
    assert UserId(42) == 42
    assert type(UserId(42)) is int
