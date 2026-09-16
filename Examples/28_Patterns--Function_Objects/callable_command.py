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

def spam() -> None:
    print("Spam, spam, spam, spam.")

macro: list[Callable[[], None]] = [
    spam,
    Repeat("Ni!", 3),
]
for command in macro:
    command()
#: Spam, spam, spam, spam.
#: Ni!
#: Ni!
#: Ni!
