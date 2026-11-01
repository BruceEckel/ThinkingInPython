# body_raises.py
import inspect
from collections.abc import Generator
from exceptions import expect

def strict() -> Generator[str, int]:
    received = yield "a positive number"
    if received <= 0:
        raise ValueError("not positive")  # [1]

g = strict()
print(next(g))
#: a positive number
expect(ValueError, g.send, -3)  # [2]
#: [ValueError] not positive
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
