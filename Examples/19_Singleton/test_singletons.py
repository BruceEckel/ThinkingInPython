# test_singletons.py
import borg_singleton
import cache_singleton
import class_variable_singleton
import config
import new_singleton
import shared_config
import singleton
import singleton_metaclass


def test_module_is_singleton() -> None:
    # shared_config did `from config import settings` and wrote to it,
    # mutating config's own dict.
    assert shared_config.settings is config.settings
    assert config.settings["theme"] == "dark"


def test_cache_factory_returns_same_instance() -> None:
    assert cache_singleton.settings() is cache_singleton.settings()


def test_new_returns_same_instance() -> None:
    assert new_singleton.OnlyOne() is new_singleton.OnlyOne()


def test_class_variable_returns_same_instance() -> None:
    a = class_variable_singleton.SingleTone("a")
    b = class_variable_singleton.SingleTone("b")
    assert a is b
    assert a.val == "b"  # Last write wins on the shared instance


def test_decorator_returns_same_instance() -> None:
    assert singleton.Foo() is singleton.Foo()


def test_metaclass_returns_same_instance() -> None:
    assert (singleton_metaclass.Bar("x")
            is singleton_metaclass.Bar("y"))


def test_borg_shares_state_but_not_identity() -> None:
    x = borg_singleton.Singleton("first")
    y = borg_singleton.Singleton("second")
    assert x is not y      # Distinct objects...
    assert x.val == y.val  # ...sharing one set of state
    assert x.val == "second"
