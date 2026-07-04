# test_weak_pool.py
from weak_pool import _pool, symbol

def test_symbols_are_shared() -> None:
    keep = symbol("x")
    assert symbol("x") is keep
    assert symbol("y") is not keep

def test_pool_releases_unused() -> None:
    temp = symbol("temp")
    assert "temp" in _pool
    del temp
    assert "temp" not in _pool
