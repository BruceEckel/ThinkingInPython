# yield_from_levels.py
from collections.abc import Generator

def inner() -> Generator[str, None, int]:
    yield "inner"
    return 42

def middle() -> Generator[str, None, int]:
    yield "middle"
    return (yield from inner())

def outer() -> Generator[str, None, int]:
    yield "outer"
    return (yield from middle())

def report() -> Generator[str]:
    result = yield from outer()
    yield f"outer returned {result}"

for line in report():
    print(line)
#: outer
#: middle
#: inner
#: outer returned 42
