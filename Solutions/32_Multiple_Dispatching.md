# Multiple Dispatching: Solutions

Both exercises use the same rule for the new `Lizard`: it beats Paper
and Scissors, and loses to Rock; Lizard versus Lizard is a draw.

## 1. Adding `Lizard` to the table version

```python
# exercise_1.py
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
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

OUTCOME: Final[dict[tuple[type[Item], type[Item]], Outcome]] = {
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
        return type(self).__name__

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
four `eval_*()` methods, one per opponent type including its own,
all of it encoding the same sixteen answers already sitting in the
table version's `OUTCOME` dictionary, just spread across four classes
instead of collected in one place. Both versions were checked against each other
while developing this solution: all sixteen combinations of the two
implementations agree.

The comparison makes the chapter's point concrete. The table costs one
class and seven dictionary rows to extend. The method version costs
one class and five new methods, plus retrofitting a method onto every
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

With this `EXPECTED` in place, `test_matches_expected()`,
parametrized over both modules, and `test_both_versions_agree()` pass
unchanged: neither hardcodes the number of item types. Both are
parametrized from `MATCHUPS`, which is built from whatever `EXPECTED`
contains, so growing it from nine entries to sixteen produces sixteen
independently reported cases per module with no change to the test
functions themselves.

## 4. Counting how often each item type appears

```python
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

OUTCOME: Final[dict[tuple[type[Item], type[Item]], Outcome]] = {
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

## 6. Making the table tolerate subclasses

```python
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

OUTCOME: Final[dict[tuple[type[Item], type[Item]], Outcome]] = {
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
```

The `KeyError` comes from a dictionary probe, which compares keys by
equality. `(Origami, Rock)` is not `(Paper, Rock)`, because `Origami`
is not `Paper`, however closely the two are related. Inheritance never
enters the lookup: a `dict` hashes the key and compares, and neither
step consults an MRO. That is what "the match is on classes exactly"
means, and it is the property `singledispatch` does not share.

The tolerant version walks both MROs and takes the first pair that has
a row, so `TolerantOrigami` finds `(TolerantPaper, TolerantRock)` one
step up on the left. What it gives up is exactly the property the
chapter names first: the match is no longer exact. Three consequences
follow, and only the first is obvious.

The lookup is no longer one probe. It is a nested loop over two MROs,
so a miss now costs the product of the two depths instead of a single
hash. For a table consulted once per duel that is nothing, and for one
consulted in an inner loop it is not.

Order now decides the answer. `(TolerantPaper, TolerantRock)` and
`(TolerantOrigami, TolerantItem)` could both match, and which one wins
depends on the order the loops happen to walk, not on anything a
reader of the table can see. The exact version has no such question:
either the pair is in the table or it is not.

The failure that made the exact version safe is gone. A `Lizard` whose
rows you forgot to write no longer raises `KeyError`; it silently
inherits its parent's answers and plays as whatever it derives from.
That is the fail-fast policy the chapter recommends for a table under
construction, traded away for the convenience of not writing rows.

Which behavior you want depends on whether a subclass is a new
competitor or a variation on an existing one. `Origami` really is
paper for the purposes of this game, and a `WetPaper` that loses to
everything is not.

## 7. A business-modeling environment

```python
# exercise_7.py
import random
from typing import Any

class Inhabitant:
    def interact(self, other: Any) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__

class Dwarf(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (engineer) negotiates with {other}"

class Elf(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (marketer) pitches to {other}"

class Troll(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (manager) directs {other}"

class Project:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def gather(self, n: int) -> list[Inhabitant]:
        kinds = [Dwarf, Elf, Troll]
        return [self.rng.choice(kinds)() for _ in range(n)]

project = Project(seed=1)
team = project.gather(4)
for a, b in zip(team, team[1:]):
    print(a.interact(b))
#: Dwarf (engineer) negotiates with Troll
#: Troll (manager) directs Dwarf
#: Dwarf (engineer) negotiates with Elf
```

This uses single dispatch, not double: `a.interact(b)` resolves on
`a`'s type only, and `other` is printed generically rather than
inspected for its own type. It becomes genuinely *double* dispatch
once `interact()`'s behavior must also vary by `other`'s type,
which is what exercise 8 adds.

## 8. Weapons, battles, and a full meeting

Six weapon types, two per `Inhabitant` kind, ranked around a cycle
(each weapon beats the next two in the ranking and loses to the
previous two, the same shape `paper_scissors_rock.py` uses for three
items, extended to six):

```python
# exercise_8.py
import random
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

WEAPON_ORDER = ["Jargon", "Play", "InventFeature",
                "SellImaginaryProduct", "Edict", "Schedule"]
WEAPON_INDEX = {name: i for i, name in enumerate(WEAPON_ORDER)}

WEAPONS_BY_KIND = {
    "Dwarf": ["Jargon", "Play"],
    "Elf": ["InventFeature", "SellImaginaryProduct"],
    "Troll": ["Edict", "Schedule"],
}

def weapon_outcome(a: str, b: str) -> Outcome:
    "A weapon beats the next two in WEAPON_ORDER (cyclically)."
    ia, ib = WEAPON_INDEX[a], WEAPON_INDEX[b]
    diff = (ia - ib) % 6
    if diff == 0:
        return Outcome.DRAW
    if diff in (1, 2):
        return Outcome.WIN
    return Outcome.LOSE

class Inhabitant2:
    KIND: str = ""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> str:
        return self.rng.choice(WEAPONS_BY_KIND[self.KIND])

class Dwarf2(Inhabitant2):
    KIND = "Dwarf"
class Elf2(Inhabitant2):
    KIND = "Elf"
class Troll2(Inhabitant2):
    KIND = "Troll"

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = weapon_outcome(a.get_weapon(), b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2, "Troll": Troll2}
        groups = {name: [cls(self.rng) for _ in range(group_size)]
                  for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

p2 = Project2(seed=3)
print(p2.meeting(group_size=5))
#: Troll
```

Since the weapon ranking is a genuine cycle (nothing dominates
everything), no group is guaranteed to win; the outcome depends on the
random weapon draws each round, the same as real rock-paper-scissors
tournaments have no fixed victor.

## 9. When the table beats the hard-coded dispatch

The table wins whenever the rules themselves are just data: a fixed
mapping from combination to outcome, with no per-combination logic
beyond "look up the answer." That describes both
`paper_scissors_rock_table.py` and this exercise's weapon rankings.
The hard-coded double dispatch earns its keep only when a specific
combination needs real code, not just a value, such as a combination
that triggers a special effect or consults outside state, something
too large to fit in one table cell.

You can keep the calling code as simple as the object version while
using a table underneath, the way `paper_scissors_rock.py`'s
`Item.compete()` and `paper_scissors_rock_table.py`'s `Item.compete()`
both read as `item1.compete(item2)` at the call site. The table only
changes what happens *inside* `compete()`, a dictionary lookup instead
of a chain of `eval_*()` calls; nothing about how a caller uses the
object changes.

## 10. Exercise 8, rebuilt on a table

```python
# exercise_10.py
import random
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

WEAPON_ORDER = ["Jargon", "Play", "InventFeature",
                "SellImaginaryProduct", "Edict", "Schedule"]

WEAPONS_BY_KIND = {
    "Dwarf": ["Jargon", "Play"],
    "Elf": ["InventFeature", "SellImaginaryProduct"],
    "Troll": ["Edict", "Schedule"],
}

def weapon_outcome(a: str, b: str) -> Outcome:
    order = WEAPON_ORDER
    diff = (order.index(a) - order.index(b)) % 6
    if diff == 0:
        return Outcome.DRAW
    return Outcome.WIN if diff in (1, 2) else Outcome.LOSE

OUTCOME_TABLE: dict[tuple[str, str], Outcome] = {
    (wa, wb): weapon_outcome(wa, wb)
    for wa in WEAPON_ORDER for wb in WEAPON_ORDER
}

class Inhabitant2:
    KIND: str = ""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> str:
        return self.rng.choice(WEAPONS_BY_KIND[self.KIND])

class Dwarf2(Inhabitant2):
    KIND = "Dwarf"
class Elf2(Inhabitant2):
    KIND = "Elf"

def battle_table(
    a: Inhabitant2, b: Inhabitant2
) -> Inhabitant2 | None:
    outcome = OUTCOME_TABLE[a.get_weapon(), b.get_weapon()]
    if outcome is Outcome.WIN:
        return a
    if outcome is Outcome.LOSE:
        return b
    return None

# Confirm the table agrees with the formula on every combination:
mismatches = [
    (wa, wb) for wa in WEAPON_ORDER for wb in WEAPON_ORDER
    if OUTCOME_TABLE[wa, wb] != weapon_outcome(wa, wb)
]
print(len(OUTCOME_TABLE), "entries, agrees with formula:",
      not mismatches)
#: 36 entries, agrees with formula: True

rng = random.Random(5)
winner = battle_table(Dwarf2(rng), Elf2(rng))
print(isinstance(winner, (Inhabitant2, type(None))))
#: True
```

`OUTCOME_TABLE` holds the same 36 answers `weapon_outcome()` computes
on the fly, one entry per ordered pair of the six weapon names.
Generating the table from the formula, rather than writing all 36
entries by hand, confirms the two agree everywhere while keeping the
lookup itself trivial: `battle_table()` no longer calls any per-weapon
logic, only indexes into a dictionary. This is the conclusion
[One Type or Many](../Chapters/32_Multiple_Dispatching.md#one-type-or-many)
reaches: the table is both shorter to write and easier to audit for a
ruleset that is fundamentally a fixed set of answers.
