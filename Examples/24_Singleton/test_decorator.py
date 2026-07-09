# test_decorator.py
import class_singleton

def test_decorator_returns_same_instance() -> None:
    assert class_singleton.Foo() is class_singleton.Foo()
