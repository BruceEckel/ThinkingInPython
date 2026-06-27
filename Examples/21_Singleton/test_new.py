# test_new.py
import new_singleton

def test_new_returns_same_instance() -> None:
    assert new_singleton.OnlyOne() is new_singleton.OnlyOne()
