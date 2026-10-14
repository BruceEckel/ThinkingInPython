# exercise_3.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def both() -> Generator[str, int]:
    yield from collect("alpha")
    yield from collect("beta")
    yield from collect("gamma")

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3, 4, 5]:
    print(f"send({value}) -> {g.send(value)}")
#: send(1) -> alpha needs another
#: alpha got 1 and 2
#: send(2) -> beta needs a value
#: send(3) -> beta needs another
#: beta got 3 and 4
#: send(4) -> gamma needs a value
#: send(5) -> gamma needs another
try:
    g.send(6)
except StopIteration:
    print("both() is exhausted")
#: gamma got 5 and 6
#: both() is exhausted
