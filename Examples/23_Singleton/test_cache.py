# test_cache.py
import cached_factory_singleton

def test_cache_factory_returns_same_instance() -> None:
    assert (cached_factory_singleton.settings() is
        cached_factory_singleton.settings())
