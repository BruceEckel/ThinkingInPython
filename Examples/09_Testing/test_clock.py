# test_clock.py
import clock

def test_stamp() -> None:
    assert clock.stamp(lambda: 100.0) == 100.0
