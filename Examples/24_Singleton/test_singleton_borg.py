# test_singleton_borg.py
from singleton_borg import Singleton

def test_borg_shares_state_but_not_identity() -> None:
    x = Singleton("first")
    y = Singleton("second")
    assert x is not y  # Distinct objects...
    assert x.val == y.val  # ...sharing one set of state
    assert x.val == "second"
