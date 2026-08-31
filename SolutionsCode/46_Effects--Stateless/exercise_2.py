# exercise_2.py
from stateless import Depend, Need, need, run, supply

class Console:
    def print(self, message: str) -> None:
        print(message)

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def greet_all(names: list[str]) -> Depend[
    Need[Console], None
]:
    for name in names:
        yield from greet(name)

run(supply(Console())(greet_all)(["Alice", "Bob"]))
#: Hello, Alice!
#: Hello, Bob!
