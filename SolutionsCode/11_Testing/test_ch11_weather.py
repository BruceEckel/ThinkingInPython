# test_ch11_weather.py
import io
import ch11_weather
import pytest

def fake_fetch(url: str) -> io.BytesIO:
    return io.BytesIO(b"21C")

def test_patched(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ch11_weather, "urlopen", fake_fetch)
    assert ch11_weather.current_temp("denver") == "21C"

def test_injected() -> None:
    got = ch11_weather.current_temp_with("denver", fake_fetch)
    assert got == "21C"
