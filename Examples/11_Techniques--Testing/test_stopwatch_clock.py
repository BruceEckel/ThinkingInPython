# test_stopwatch_clock.py
import stopwatch_clock

def test_elapsed() -> None:
    assert stopwatch_clock.elapsed(
        40.0, lambda: 100.0) == 60.0
