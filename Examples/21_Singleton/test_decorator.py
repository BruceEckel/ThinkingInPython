# test_decorator.py
import singleton

def test_decorator_returns_same_instance() -> None:
    assert singleton.Foo() is singleton.Foo()
