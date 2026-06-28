# test_cache.py
import cache_singleton

def test_cache_factory_returns_same_instance() -> None:
    assert cache_singleton.settings() is cache_singleton.settings()
