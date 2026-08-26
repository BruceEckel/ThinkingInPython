# exercise_4.py
import random
from collections import Counter
from collections.abc import Iterator
from enum import StrEnum
from typing import Any, Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, item: Item) -> Outcome:
        return OUTCOME[type(self), type(item)]

    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Outcome]] = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Paper, Lizard): Outcome.LOSE,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Scissors, Lizard): Outcome.LOSE,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
  (Rock, Lizard): Outcome.WIN,
  (Lizard, Paper): Outcome.WIN,
  (Lizard, Scissors): Outcome.WIN,
  (Lizard, Rock): Outcome.LOSE,
  (Lizard, Lizard): Outcome.DRAW,
}

def duel(item1: Any, item2: Any) -> None:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")

random.seed(47)

def item_pair_gen[T](base: type[T], n: int,
                     counts: Counter[str] | None = None
                     ) -> Iterator[tuple[T, T]]:
    if counts is None:
        counts = Counter()
    items = base.__subclasses__()
    for _ in range(n):
        a, b = (random.choice(items)(),
                random.choice(items)())
        counts[type(a).__name__] += 1
        counts[type(b).__name__] += 1
        yield a, b

counts: Counter[str] = Counter()
for item1, item2 in item_pair_gen(Item, 100, counts):
    pass  # duel(item1, item2) in the real version
print(counts["Lizard"])
#: 53
