# exercise_6.py
from enum import StrEnum
from typing import Final

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
class Rock(Item):
    pass

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Outcome]] = {
    (Paper, Rock): Outcome.WIN,
    (Rock, Paper): Outcome.LOSE,
}

class Origami(Paper):
    pass

try:
    Origami().compete(Rock())
except KeyError as e:
    print(type(e).__name__, [c.__name__ for c in e.args[0]])
#: KeyError ['Origami', 'Rock']

class TolerantItem(Item):
    def compete(self, item: Item) -> Outcome:
        for left in type(self).__mro__:
            for right in type(item).__mro__:
                if not (issubclass(left, Item)
                        and issubclass(right, Item)):
                    continue  # object is not an Item
                if (left, right) in OUTCOME:
                    return OUTCOME[left, right]
        raise KeyError((type(self), type(item)))

class TolerantPaper(TolerantItem):
    pass
class TolerantRock(TolerantItem):
    pass
class TolerantOrigami(TolerantPaper):
    pass

OUTCOME[TolerantPaper, TolerantRock] = Outcome.WIN
OUTCOME[TolerantRock, TolerantPaper] = Outcome.LOSE

print(TolerantOrigami().compete(TolerantRock()))
#: win
