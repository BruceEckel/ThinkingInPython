# test_weak_pool.py
from weak_pool import _pool, name

def test_names_are_shared() -> None:
    keep = name("x")
    assert name("x") is keep
    assert name("y") is not keep

def test_pool_releases_unused() -> None:
    temp = name("temp")
    assert "temp" in _pool
    del temp
    assert "temp" not in _pool
