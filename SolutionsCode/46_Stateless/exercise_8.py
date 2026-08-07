# exercise_8.py
from collections.abc import Callable
from functools import partial
from typing import Final
from stateless import Depend, Need, Success, need, run, supply

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

NAMES: Final[list[str]] = ["Alice", "Bob"]

built: dict[str, Success[None]] = {
    name: supply(Console())(greet)(name) for name in NAMES
}
for effect in built.values():
    run(effect)
#: Hello, Alice!
#: Hello, Bob!
for effect in built.values():  # The same objects, a second time
    run(effect)

def make(name: str) -> Success[None]:
    return supply(Console())(greet)(name)

builders: dict[str, Callable[[], Success[None]]] = {
    name: partial(make, name) for name in NAMES
}
for builder in builders.values():
    run(builder())
#: Hello, Alice!
#: Hello, Bob!
for builder in builders.values():  # A fresh Effect each time
    run(builder())
#: Hello, Alice!
#: Hello, Bob!
