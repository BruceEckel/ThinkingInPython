# tail_delegation.py
from collections.abc import Generator
from exceptions import expect

def tick() -> Generator[str]:
    yield "tick"
    return (yield from tock())  # [1]

def tock() -> Generator[str]:
    yield "tock"
    return (yield from tick())

def run(steps: int) -> None:
    clock = tick()
    for _ in range(steps):
        next(clock)

run(500)
expect(RecursionError, run, 2000)
#: [RecursionError] maximum recursion depth exceeded
