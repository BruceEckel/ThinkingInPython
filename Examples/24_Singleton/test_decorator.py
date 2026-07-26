# test_decorator.py
from singleton_class import Foo

def test_decorator_returns_same_instance() -> None:
    assert Foo() is Foo()
