# test_framework.py
from template_function import run_framework
from template_method import ApplicationFramework


def test_template_method_runs_steps_in_order() -> None:
    calls: list[str] = []

    class Recorder(ApplicationFramework):
        def customize1(self) -> None:
            calls.append("one")

        def customize2(self) -> None:
            calls.append("two")

    Recorder()  # constructing it runs the framework
    assert calls == ["one", "two", "one", "two"]  # loop runs twice


def test_template_function_runs_steps_in_order() -> None:
    calls: list[str] = []
    run_framework(
        lambda: calls.append("a"), lambda: calls.append("b"))
    assert calls == ["a", "b", "a", "b"]
