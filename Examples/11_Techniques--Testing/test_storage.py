# test_storage.py
from pathlib import Path
import pytest
import storage

@pytest.fixture(autouse=True)
def app_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_DATA", str(tmp_path))

def test_round_trip() -> None:
    storage.save("greeting.txt", "hello")
    assert storage.load("greeting.txt") == "hello"

def test_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        storage.load("absent.txt")
