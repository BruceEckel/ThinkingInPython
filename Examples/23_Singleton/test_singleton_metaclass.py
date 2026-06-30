# test_singleton_metaclass.py
import singleton_metaclass

def test_metaclass_returns_same_instance() -> None:
    assert (singleton_metaclass.Bar("x")
            is singleton_metaclass.Bar("y"))
