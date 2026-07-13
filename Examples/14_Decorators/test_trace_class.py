# test_trace_class.py
from trace_class import trace

def test_trace_preserves_name() -> None:
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add.__name__ == "add"

def test_trace_returns_original_result() -> None:
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
