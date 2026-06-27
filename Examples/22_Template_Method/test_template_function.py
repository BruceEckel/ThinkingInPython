# test_template_function.py
from template_function import run_framework

def test_template_function_runs_steps_in_order() -> None:
    calls: list[str] = []
    run_framework(
        lambda: calls.append("a"), lambda: calls.append("b"))
    assert calls == ["a", "b", "a", "b"]
