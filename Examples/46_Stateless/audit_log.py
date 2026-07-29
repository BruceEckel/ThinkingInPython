# audit_log.py
from dataclasses import dataclass, field
from greeter import Console, greet
from stateless import Depend, Need, need, run, supply

@dataclass
class Log:
    entries: list[str] = field(default_factory=list)
    def write(self, entry: str) -> None:
        self.entries.append(entry)

def greet_logged(
    name: str,
) -> Depend[Need[Console] | Need[Log], None]:
    yield from greet(name)
    log = yield from need(Log)
    log.write(f"greeted {name}")

def greet_all(
    names: list[str],
) -> Depend[Need[Console] | Need[Log], None]:
    for name in names:
        yield from greet_logged(name)

log = Log()
run(supply(Console(), log)(greet_all)(["Alice", "Bob"]))
print(log.entries)
#: Hello, Alice!
#: Hello, Bob!
#: ['greeted Alice', 'greeted Bob']
