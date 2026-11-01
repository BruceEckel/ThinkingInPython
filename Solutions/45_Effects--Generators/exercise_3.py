# exercise_3.py
from collections.abc import Generator
from typing import NewType

Prompt = NewType("Prompt", str)
type Value = int
Total = NewType("Total", int)

def collect(name: str) -> Generator[Prompt, Value, Total]:
    first: Value = yield Prompt(f"{name} needs a value")
    second: Value = yield Prompt(f"{name} needs another")
    print(f"{name} got {first} and {second}")
    return Total(first + second)

def both() -> Generator[Prompt, Value]:
    alpha: Total = yield from collect("alpha")
    beta: Total = yield from collect("beta")
    gamma: Total = yield from collect("gamma")
    yield Prompt(f"total {alpha + beta + gamma}")

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3, 4, 5, 6]:
    print(f"g.send({value}) -> {g.send(value)}")
#: g.send(1) -> alpha needs another
#: alpha got 1 and 2
#: g.send(2) -> beta needs a value
#: g.send(3) -> beta needs another
#: beta got 3 and 4
#: g.send(4) -> gamma needs a value
#: g.send(5) -> gamma needs another
#: gamma got 5 and 6
#: g.send(6) -> total 21
