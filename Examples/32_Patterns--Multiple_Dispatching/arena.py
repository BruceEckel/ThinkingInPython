# arena.py
from collections.abc import Iterator
from itertools import product
from typing import Any

def all_pairs[T](base: type[T]) -> Iterator[tuple[T, T]]:
    kinds = base.__subclasses__()
    for a, b in product(kinds, kinds):
        yield a(), b()

def duel(player: Any, opponent: Any) -> None:
    result = player.compete(opponent)
    print(f"{player} <--> {opponent} : {result}")
