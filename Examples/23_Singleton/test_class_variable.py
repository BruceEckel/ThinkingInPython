# test_class_variable.py
import class_variable_singleton

def test_class_variable_returns_same_instance() -> None:
    a = class_variable_singleton.CVSingleton("a")
    b = class_variable_singleton.CVSingleton("b")
    assert a is b
    assert a.val == "b"  # Last write wins on the shared instance
