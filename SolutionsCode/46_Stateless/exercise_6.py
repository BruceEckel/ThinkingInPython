# exercise_6.py
from dataclasses import dataclass
from stateless import Depend, Need, handle, need, run

@dataclass
class Console:
    def print(self, message: str) -> None:
        print(message)

@dataclass
class Clock:
    def now(self) -> str:
        return "noon"

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def stamped(
    name: str,
) -> Depend[Need[Console] | Need[Clock], None]:
    clock = yield from need(Clock)
    console = yield from need(Console)
    console.print(f"[{clock.now()}] Hello, {name}!")

def default(ability: Need[Console]) -> Console:
    print(f"handler answered a request "
          f"for {ability.t.__name__}")
    return ability.t()

defaults = handle(default)
run(defaults(greet)("Alice"))
#: handler answered a request for Console
#: Hello, Alice!
run(defaults(stamped)("Bob"))  # type: ignore
#: handler answered a request for Clock
#: handler answered a request for Console
#: [noon] Hello, Bob!
