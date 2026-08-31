# test_singleton_class.py
import pytest
from singleton_class import Registry

def test_isinstance_rejects_the_decorated_name() -> None:
    with pytest.raises(TypeError,
                       match="arg 2 must be a type"):
        isinstance(Registry("primary"), Registry)  # type: ignore

def test_subclassing_the_decorated_name_fails() -> None:
    with pytest.raises(TypeError,
                       match="takes 2 positional"):
        class Sub(Registry):  # type: ignore
            pass
