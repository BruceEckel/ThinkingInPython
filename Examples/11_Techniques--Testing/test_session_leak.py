# test_session_leak.py
import pytest

@pytest.fixture(scope="session")
def shared_cache() -> dict[str, int]:
    return {}

def test_first_write(
    shared_cache: dict[str, int]
) -> None:
    shared_cache["seen"] = 1
    assert shared_cache == {"seen": 1}

def test_second_sees_leftover(
    shared_cache: dict[str, int]
) -> None:
    assert shared_cache == {"seen": 1}
