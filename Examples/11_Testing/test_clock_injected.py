# test_clock_injected.py
import clock_injected

def test_elapsed() -> None:
    assert clock_injected.elapsed(
        40.0, lambda: 100.0) == 60.0
