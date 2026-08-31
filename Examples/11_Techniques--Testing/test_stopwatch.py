# test_stopwatch.py
import time
import pytest
import stopwatch

def test_elapsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "time", lambda: 100.0)
    assert stopwatch.elapsed(40.0) == 60.0
