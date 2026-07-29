# yield_from_send.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def both() -> Generator[str, int]:
    yield from collect("alpha")
    yield from collect("beta")

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3]:
    print(g.send(value))
#: alpha needs another
#: alpha got 1 and 2
#: beta needs a value
#: beta needs another
try:
    g.send(4)
except StopIteration:
    print("both() is exhausted")
#: beta got 3 and 4
#: both() is exhausted
