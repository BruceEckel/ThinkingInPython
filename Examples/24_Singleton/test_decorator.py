# test_decorator.py
from singleton_class import Registry

def test_decorator_returns_same_instance() -> None:
    assert Registry("a") is Registry("b")
