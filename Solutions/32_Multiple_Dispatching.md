# Multiple Dispatching: Solutions

Both exercises use the same rule for the new `Lizard`: it beats Paper
and Scissors, and loses to Rock; Lizard versus Lizard is a draw.

## 1. Adding `Lizard` to the table version

```python
# exercise_1.py
from enum import StrEnum
from typing import Any, Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, item: Any) -> Outcome:
        return OUTCOME[self.__class__, item.__class__]

    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

OUTCOME: Final[dict[tuple[type, type], Outcome]] = {
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

print(Lizard().compete(Paper()), Rock().compete(Lizard()))
#: win win
```

Sixteen entries cover the four types against each other (4 × 4), the
same shape as the original nine (3 × 3). Adding a fourth `Item` cost
one class declaration and seven new dictionary rows (the six new
ordered pairs `Lizard` forms with the other three, plus
`(Lizard, Lizard)`); `compete()` itself needed no change.

## 2. Adding `Lizard` to the double-dispatch version

```python
# exercise_2.py
from enum import StrEnum
from typing import Any

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item: Any) -> Outcome:
        return item.eval_paper(self)

    def eval_paper(self, item: Any) -> Outcome:
        return Outcome.DRAW

    def eval_scissors(self, item: Any) -> Outcome:
        return Outcome.WIN

    def eval_rock(self, item: Any) -> Outcome:
        return Outcome.LOSE

    def eval_lizard(self, item: Any) -> Outcome:
        return Outcome.WIN

class Scissors(Item):
    def compete(self, item: Any) -> Outcome:
        return item.eval_scissors(self)

    def eval_paper(self, item: Any) -> Outcome:
        return Outcome.LOSE

    def eval_scissors(self, item: Any) -> Outcome:
        return Outcome.DRAW

    def eval_rock(self, item: Any) -> Outcome:
        return Outcome.WIN

    def eval_lizard(self, item: Any) -> Outcome:
        return Outcome.WIN

class Rock(Item):
    def compete(self, item: Any) -> Outcome:
        return item.eval_rock(self)

    def eval_paper(self, item: Any) -> Outcome:
        return Outcome.WIN

    def eval_scissors(self, item: Any) -> Outcome:
        return Outcome.LOSE

    def eval_rock(self, item: Any) -> Outcome:
        return Outcome.DRAW

    def eval_lizard(self, item: Any) -> Outcome:
        return Outcome.LOSE

class Lizard(Item):
    def compete(self, item: Any) -> Outcome:
        return item.eval_lizard(self)

    def eval_paper(self, item: Any) -> Outcome:
        return Outcome.LOSE

    def eval_scissors(self, item: Any) -> Outcome:
        return Outcome.LOSE

    def eval_rock(self, item: Any) -> Outcome:
        return Outcome.WIN

    def eval_lizard(self, item: Any) -> Outcome:
        return Outcome.DRAW

print(Lizard().compete(Paper()), Lizard().compete(Scissors()),
      Lizard().compete(Rock()), Lizard().compete(Lizard()))
#: win win lose draw
```

This version costs far more to extend. Every *existing* class
(`Paper`, `Scissors`, `Rock`) needs a brand-new `eval_lizard()` method,
one line each, and the new `Lizard` class needs a `compete()` plus
three more `eval_*()` methods, one per opponent type, all four
encoding the same nine numbers already sitting in the table version's
`OUTCOME` dictionary, just spread across four classes instead of
collected in one place. Both versions were checked against each other
while developing this solution: all sixteen combinations of the two
implementations agree.

The comparison makes the chapter's point concrete. The table costs one
class and seven dictionary rows to extend. The method version costs
one class and four new methods, plus retrofitting a method onto every
class that already existed. That cost only grows as more item types
are added, which is exactly why the chapter recommends the table for
data that is mostly pure lookup, and reserves the method version for
combinations that need real, type-specific logic too large for one
table cell.

## 3. Sixteen matchups in `EXPECTED`

```python
# exercise_3.py
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

EXPECTED: Final[dict[tuple[str, str], Outcome]] = {
    ("Paper", "Rock"): Outcome.WIN,
    ("Paper", "Scissors"): Outcome.LOSE,
    ("Paper", "Paper"): Outcome.DRAW,
    ("Paper", "Lizard"): Outcome.LOSE,
    ("Scissors", "Paper"): Outcome.WIN,
    ("Scissors", "Rock"): Outcome.LOSE,
    ("Scissors", "Scissors"): Outcome.DRAW,
    ("Scissors", "Lizard"): Outcome.LOSE,
    ("Rock", "Scissors"): Outcome.WIN,
    ("Rock", "Paper"): Outcome.LOSE,
    ("Rock", "Rock"): Outcome.DRAW,
    ("Rock", "Lizard"): Outcome.WIN,
    ("Lizard", "Paper"): Outcome.WIN,
    ("Lizard", "Scissors"): Outcome.WIN,
    ("Lizard", "Rock"): Outcome.LOSE,
    ("Lizard", "Lizard"): Outcome.DRAW,
}

print(len(EXPECTED))
#: 16
```

With this `EXPECTED` in place, `test_table_version_matches_expected()`,
`test_method_version_matches_expected()`, and
`test_both_versions_agree()` all pass unchanged: none of the three
tests hardcodes the number of item types, only iterates over whatever
`EXPECTED` contains, so growing it from nine entries to sixteen tests
more combinations with no change to the test functions themselves.

## 4. Counting how often each item type appears

```python
# exercise_4.py
import random
from collections import Counter
from collections.abc import Iterator
from enum import StrEnum
from typing import Any

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, item: Any) -> Outcome:
        return OUTCOME[self.__class__, item.__class__]

    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

OUTCOME: dict[tuple[type, type], Outcome] = {
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

def item_pair_gen(base: type, n: int,
                   counts: Counter[str] | None = None
                   ) -> Iterator[tuple[Any, Any]]:
    if counts is None:
        counts = Counter()
    items = base.__subclasses__()
    for _ in range(n):
        a, b = random.choice(items)(), random.choice(items)()
        counts[type(a).__name__] += 1
        counts[type(b).__name__] += 1
        yield a, b

counts: Counter[str] = Counter()
for item1, item2 in item_pair_gen(Item, 100, counts):
    pass  # duel(item1, item2) in the real version
print(counts["Lizard"])
#: 53
```

`counts` is an optional parameter with a default of `None`, so every
existing call such as `item_pair_gen(Item, 10)` still works exactly as
before, unpacking a plain `(item1, item2)` pair each time. Only a
caller that wants the tally needs to pass its own `Counter` in; the
generator then updates that same object in place on every pair it
produces, one increment per item, so the caller can read
`counts["Lizard"]` at any point during or after the loop, without
`item_pair_gen()` needing to change what it yields.

## 5. `__sub__()` and `__rsub__()` on `Meters`

```python
# exercise_5.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Meters:
    n: float

    def __sub__(self, other: object) -> Meters:
        if isinstance(other, Meters):
            return Meters(self.n - other.n)
        if isinstance(other, int | float):
            return Meters(self.n - other)
        return NotImplemented

    def __rsub__(self, other: object) -> Meters:
        if isinstance(other, int | float):
            return Meters(other - self.n)  # Not self.n - other
        return NotImplemented

print(Meters(10) - Meters(3), Meters(10) - 3)
#: Meters(n=7) Meters(n=7)
print(10 - Meters(3))
#: Meters(n=7)
try:
    "ten" - Meters(3)
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

`__sub__()` is `__add__()` with the sign changed, and the three cases
line up the same way: a `Meters`, a number, or `NotImplemented` for
anything else. `__rsub__()` needs only the numeric case, because
Python asks the left operand first and `Meters(10) - Meters(3)` is
answered there. The reflected form is reached only when the left
operand declined, which two `Meters` never do.

The swap is where subtraction differs from addition. Python calls
`Meters.__rsub__(Meters(3), 10)` for the expression `10 - Meters(3)`,
so `self` is the right operand and `other` is the left one, and the
method has to put them back in the order the source wrote them.
`Meters(other - self.n)` gives `Meters(7)`. Writing
`Meters(self.n - other)`, the same body `__sub__()` uses, would give
`Meters(-7)`: a correct-looking method that quietly returns the
negative of every reflected subtraction. `__radd__()` hides this
because addition commutes, so the mistake costs nothing there and
costs the wrong answer here.

`"ten" - Meters(3)` finds no `str.__sub__` at all, so Python goes
straight to `Meters.__rsub__`, which returns `NotImplemented` for a
`str`. With both sides declining, Python raises the `TypeError`, and
the message names both types. Returning `NotImplemented` rather than
raising an exception is what makes that message possible: an exception
raised inside `__rsub__()` would report `Meters`'s complaint instead of
Python's account of which pair of types has no defined subtraction.
