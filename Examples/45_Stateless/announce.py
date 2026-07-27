# announce.py
from greeter import Console
from scores import score
from stateless import Effect, Need, need

def announce(name: str) -> Effect[Need[Console], KeyError, None]:
    value = yield from score(name)
    console = yield from need(Console)
    console.print(f"{name}: {value}")
