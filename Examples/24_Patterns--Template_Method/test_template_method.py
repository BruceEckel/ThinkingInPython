# test_template_method.py
from typing import override
from framework import ApplicationFramework

def test_template_method_runs_steps_in_order() -> None:
    calls: list[str] = []

    class Recorder(ApplicationFramework):
        @override
        def customize1(self) -> None:
            calls.append("one")

        @override
        def customize2(self) -> None:
            calls.append("two")

    app = Recorder()
    assert calls == []
    app.run()
    assert calls == ["one", "two", "one", "two"]
