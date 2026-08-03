# catch_score.py
from typing import assert_never
from greeter import Console
from scores import score
from stateless import Depend, Need, catch, need, run, supply

def report(name: str) -> Depend[Need[Console], None]:
    value: int | KeyError = yield from catch(KeyError)(score)(name)
    console = yield from need(Console)
    match value:
        case KeyError():
            console.print(f"{name}: unknown")
        case int():
            console.print(f"{name}: {value}")
        case _:
            assert_never(value)

run(supply(Console())(report)("Alice"))
run(supply(Console())(report)("Carol"))
#: Alice: 42
#: Carol: unknown
