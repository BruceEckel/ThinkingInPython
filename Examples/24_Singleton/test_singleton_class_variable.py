# test_singleton_class_variable.py
from singleton_class_variable import CVSingleton

def test_class_variable_returns_same_instance() -> None:
    a = CVSingleton("a")
    b = CVSingleton("b")
    assert a is b
    assert a.val == "b"  # Last write wins on the shared instance
