# test_object_pool.py
import pytest
from object_pool import Connection, Pool

def test_lease_removes_then_returns() -> None:
    pool = Pool(Connection(1), Connection(2))
    with pool.lease():
        assert pool.available() == 1
    assert pool.available() == 2

def test_returned_on_exception() -> None:
    pool = Pool(Connection(1))
    with pytest.raises(RuntimeError):
        with pool.lease():
            raise RuntimeError("boom")
    assert pool.available() == 1

def test_objects_reused_not_recreated() -> None:
    pool = Pool(Connection(1))
    with pool.lease() as first:
        pass
    with pool.lease() as second:
        assert second is first
