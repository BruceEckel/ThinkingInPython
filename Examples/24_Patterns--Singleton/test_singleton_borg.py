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
    assert x.__dict__ is y.__dict__
    assert x.val == "second"

def test_leaves_an_attribute_behind() -> None:
    setattr(Singleton("first"), "extra", "leftover")

def test_fixture_clears_shared_state() -> None:
    y = Singleton("second")
    assert not hasattr(y, "extra")  # Reset ran
