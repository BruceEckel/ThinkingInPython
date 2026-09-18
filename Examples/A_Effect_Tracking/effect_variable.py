# effect_variable.py
from collections.abc import Callable
from typing import Any
from stateless import (
    Ability,
    Depend,
    Need,
    need,
    run,
    supply,
)

class Console:
    def print(self, message: str) -> None:
        print(message)

def hello() -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print("Hello!")

def twice[A: Ability[Any]](
    effect: Callable[[], Depend[A, None]],
) -> Depend[A, None]:
    yield from effect()
    yield from effect()

def hello_twice() -> Depend[Need[Console], None]:
    yield from twice(hello)

run(supply(Console())(hello_twice)())
#: Hello!
#: Hello!
