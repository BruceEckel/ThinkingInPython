# side_effect.py
from stateless import Depend, Need, need, run, supply
from stateless.console import Console

def display(n: int) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(n)

bound = supply(Console())(display)
run(bound(42))
#: 42
