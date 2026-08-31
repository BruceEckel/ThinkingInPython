# exercise_12.py
import random
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

@dataclass(frozen=True)
class Random(Ability[int]):
    low: int
    high: int

def roll(low: int, high: int) -> Depend[Random, int]:
    return (yield Random(low, high))

def game() -> Depend[Random, str]:
    first = yield from roll(1, 6)
    second = yield from roll(1, 6)
    return f"{first} + {second} = {first + second}"

def real(request: Random) -> int:
    return random.randint(request.low, request.high)

def scripted_from(
    values: Iterator[int],
) -> Callable[[Random], int]:
    def scripted(request: Random) -> int:
        return next(values)
    return scripted

random.seed(0)
print(run(handle(real)(game)()))
#: 4 + 4 = 8
print(run(handle(scripted_from(iter([3, 4])))(game)()))
#: 3 + 4 = 7
