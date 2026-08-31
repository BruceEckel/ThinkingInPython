# arena.py
import random
from collections.abc import Iterator
from typing import Any

def item_pair_gen[T](base: type[T],
                     n: int) -> Iterator[tuple[T, T]]:
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()

def duel(item1: Any, item2: Any) -> None:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
