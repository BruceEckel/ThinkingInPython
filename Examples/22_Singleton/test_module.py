# test_module.py
import config
import shared_config

def test_module_is_singleton() -> None:
    # shared_config did `from config import settings` and wrote to it,
    # mutating config's own dict.
    assert shared_config.settings is config.settings
    assert config.settings["theme"] == "dark"
