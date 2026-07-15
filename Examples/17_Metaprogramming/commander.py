# commander.py
from collections.abc import Callable
from typing import ClassVar, cast
from exceptions import ignore

class Command:
    KNOWN_COMMANDS: ClassVar[set[str]] = {"Start", "Stop", "Pause"}

    def __init__(self, label: str) -> None:
        self.label = label

    def run(self) -> str:
        return f"Running {self.label}"

    @classmethod
    def make_class(cls, class_name: str) -> Callable[[], Command]:
        if class_name not in cls.KNOWN_COMMANDS:
            raise ValueError(f"Unknown command: {class_name!r}")
        klass = f"""
class {class_name}(Command):
    def __init__(self) -> None:
        super().__init__("{class_name}")
"""
        namespace: dict[str, type[Command]] = {"Command": Command}
        exec(klass, namespace)
        return cast(Callable[[], Command], namespace[class_name])

if __name__ == "__main__":
    for name in ("Start", "Stop", "Pause"):
        command_class = Command.make_class(name)
        print(command_class().run())
    with ignore(ValueError):
        Command.make_class("Reset")
#: Running Start
#: Running Stop
#: Running Pause
#: ignoring ValueError("Unknown command: 'Reset'")
