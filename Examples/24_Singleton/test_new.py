# test_new.py
from singleton_with_new import OnlyOne

def test_new_returns_same_instance() -> None:
    assert OnlyOne() is OnlyOne()
