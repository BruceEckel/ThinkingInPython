# yield_from_send.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int, int]:
    first = yield f"{name} needs a value"  # [1]
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")
    return first + second

def both() -> Generator[str, int]:
    alpha = yield from collect("alpha")  # [2]
    beta = yield from collect("beta")  # [3]
    yield f"total {alpha + beta}"  # [4]

g = both()
print(next(g))
#: alpha needs a value
for value in [1, 2, 3, 4]:
    print(f"send({value}) -> {g.send(value)}")
#: send(1) -> alpha needs another
#: alpha got 1 and 2
#: send(2) -> beta needs a value
#: send(3) -> beta needs another
#: beta got 3 and 4
#: send(4) -> total 10
