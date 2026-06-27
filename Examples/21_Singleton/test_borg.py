# test_borg.py
import borg_singleton

def test_borg_shares_state_but_not_identity() -> None:
    x = borg_singleton.Singleton("first")
    y = borg_singleton.Singleton("second")
    assert x is not y      # Distinct objects...
    assert x.val == y.val  # ...sharing one set of state
    assert x.val == "second"
