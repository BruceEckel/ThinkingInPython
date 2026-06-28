# test_weather.py
import io
import pytest
import weather

def test_current_temp(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str) -> io.BytesIO:
        return io.BytesIO(b"21C")
    monkeypatch.setattr(weather, "urlopen", fake_urlopen)
    assert weather.current_temp("denver") == "21C"
