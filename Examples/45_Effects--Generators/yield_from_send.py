# yield_from_send.py
from collections.abc import Generator
from collect import Prompt, Total, Value, collect

def both() -> Generator[Prompt, Value]:
    alpha: Total = yield from collect("alpha")  # [1]
    beta: Total = yield from collect("beta")  # [2]
    yield Prompt(f"total {alpha + beta}")  # [3]

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
