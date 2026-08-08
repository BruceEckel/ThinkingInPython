# ch17_exec_injection.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

@dataclass
class Command:
    label: str

    def run(self) -> str:
        return f"Running {self.label}"

    @classmethod
    def make_class(cls, class_name: str) -> Callable[[], Command]:
        # The KNOWN_COMMANDS check has been removed:
        klass = f"""
class {class_name}(Command):
    def __init__(self) -> None:
        super().__init__("{class_name}")
"""
        namespace: dict[str, Any] = {"Command": Command}
        exec(klass, namespace)
        return cast(Callable[[], Command], namespace[class_name])

attack = (
    'X(Command):\n'
    '    pass\n'
    'print("injected code ran")\n'
    'Y = """  #'
)
try:
    Command.make_class(attack)
except KeyError:
    print("lookup failed, after the injection ran")
#: injected code ran
#: lookup failed, after the injection ran
