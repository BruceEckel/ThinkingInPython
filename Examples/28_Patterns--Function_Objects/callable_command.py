# callable_command.py
from collections.abc import Callable
from record import record

type Command = Callable[[], None]

@record
class Repeat:
    text: str
    times: int
    def __call__(self) -> None:
        for _ in range(self.times):
            print(self.text)

def spam() -> None:
    print("Spam, eggs, sausage, spam.")

macro: list[Command] = [
    spam,
    Repeat("Ni!", 3),
]
for command in macro:
    command()
#: Spam, eggs, sausage, spam.
#: Ni!
#: Ni!
#: Ni!
