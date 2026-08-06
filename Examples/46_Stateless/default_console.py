# default_console.py
from dataclasses import dataclass
from stateless import Depend, Need, need, run, supply

@dataclass
class Console:
    tag: str
    def print(self, message: str) -> None:
        print(f"[{self.tag}] {message}")

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

fallback = supply(Console("default"))
run(fallback(greet)("Alice"))
#: [default] Hello, Alice!
chosen = supply(Console("chosen"))(greet)
run(fallback(chosen)("Bob"))
#: [chosen] Hello, Bob!
