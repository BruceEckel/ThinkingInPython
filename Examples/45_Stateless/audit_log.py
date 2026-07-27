# audit_log.py
from greeter import Console, greet
from stateless import Depend, Need, need, run, supply

class Log:
    def __init__(self) -> None:
        self.entries: list[str] = []
    def write(self, entry: str) -> None:
        self.entries.append(entry)

type Greeting = Depend[Need[Console] | Need[Log], None]

def greet_logged(name: str) -> Greeting:
    yield from greet(name)
    log = yield from need(Log)
    log.write(f"greeted {name}")

def greet_all(names: list[str]) -> Greeting:
    for name in names:
        yield from greet_logged(name)

log = Log()
run(supply(Console(), log)(greet_all)(["Alice", "Bob"]))
print(log.entries)
#: Hello, Alice!
#: Hello, Bob!
#: ['greeted Alice', 'greeted Bob']
