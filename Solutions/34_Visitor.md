# Visitor: Solutions

## 1. A business-modeling environment

```python
# exercise_1.py
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
which is exactly what exercise 2 adds.

## 2. Weapons, battles, and a full meeting

Six weapon types, two per `Inhabitant` kind, ranked around a cycle
(each weapon beats the next two in the ranking and loses to the
previous two, the same shape `paper_scissors_rock.py` uses for three
items, extended to six):

```python
# exercise_2.py
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

## 3. When the table beats the hard-coded dispatch

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

## 4. Exercise 2, rebuilt on a table

```python
# exercise_4.py
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
logic, only indexes into a dictionary. This is
[Multiple Dispatching](33_Multiple_Dispatching.md#one-type-or-many)'s
own conclusion: the table is both shorter to write and easier to
audit for a ruleset that is fundamentally a fixed set of answers.
