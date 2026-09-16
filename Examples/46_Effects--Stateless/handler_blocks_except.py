# handler_blocks_except.py
from exceptions import expect
from greeter import Console
from scores import score
from stateless import Effect, Need, need, run, supply

def guarded(
    name: str
) -> Effect[Need[Console], KeyError, str]:
    try:
        value = yield from score(name)
    except KeyError:
        return f"{name}: unknown"
    console = yield from need(Console)
    console.print(f"{name}: {value}")
    return f"{name}: {value}"

expect(KeyError, run, supply(Console())(guarded)("Carol"))
#: [KeyError] 'Carol'
