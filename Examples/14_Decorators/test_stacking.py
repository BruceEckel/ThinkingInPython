# test_stacking.py
from repeat_class import repeat
from trace_class import trace

def test_stacked_decorators_preserve_name() -> None:
    @trace
    @repeat(times=2)
    def greet(name: str) -> str:
        return name

    assert greet.__name__ == "greet"

def test_stacked_decorators_repeat_the_call() -> None:
    calls: list[str] = []

    @trace
    @repeat(times=2)
    def record() -> None:
        calls.append("call")

    record()
    assert calls == ["call", "call"]
