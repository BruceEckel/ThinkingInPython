# callable_command.py
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Repeat:
    text: str
    times: int
    def __call__(self) -> None:
        for _ in range(self.times):
            print(self.text)

macro: list[Callable[[], None]] = [
    Repeat("You're a loony.", 1),
    Repeat("Say no more.", 2),
]
for command in macro:
    command()
#: You're a loony.
#: Say no more.
#: Say no more.
