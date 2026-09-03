# test_singleton_borg.py
import pytest
from singleton_borg import Borg, Singleton

@pytest.fixture(autouse=True)
def reset_shared_state() -> None:
    Borg._shared_state.clear()

def test_borg_shares_state_but_not_identity() -> None:
    x = Singleton("first")
    y = Singleton("second")
    assert x is not y  # Distinct objects
    assert x.val == y.val  # But sharing one set of state
    assert x.val == "second"

def test_pollutes_shared_state() -> None:
    setattr(Singleton("first"), "extra", "leftover")

def test_fixture_cleared_it() -> None:
    y = Singleton("second")
    assert not hasattr(y, "extra")  # Reset ran
