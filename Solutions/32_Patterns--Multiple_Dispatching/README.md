# Multiple Dispatching: Solutions

Every exercise that adds `Lizard` uses the same rule: `Lizard` beats
Paper and Scissors, and loses to Rock. Lizard versus Lizard is a draw.

## 1. Adding `Lizard` to the table version

> Add a fourth `Item`, `Lizard`, to `paper_scissors_rock_table.py`.
> Lizard beats Paper and Scissors, and loses to Rock.
> Lizard versus Lizard is a draw.
> Add the seven new entries that `OUTCOME` needs:
> both orders of each mixed pair, plus Lizard versus Lizard.

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

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
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

if __name__ == "__main__":
    print(Lizard().compete(Paper()),
          Rock().compete(Lizard()))
#: win win
```

Sixteen entries cover the four types against each other (4 × 4), the
same shape as the original nine (3 × 3). Adding a fourth `Item` costs
one class declaration and seven new dictionary rows (the six new
ordered pairs `Lizard` forms with the other three, plus
`(Lizard, Lizard)`). `compete()` needs no change.
The `__main__` guard lets exercise 3 import this module without
running its demonstration, as the chapter's own two versions do.

## 2. Adding `Lizard` to the double-dispatch version

> Add the same `Lizard` to `paper_scissors_rock.py`,
> the double-dispatch version,
> which means adding an `eval_lizard()` method to every existing class,
> plus a `Lizard` class with its own `compete()` and four `eval_*()` methods.
> Compare how much code this took versus adding `Lizard` to the table version.

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

if __name__ == "__main__":
    print(Lizard().compete(Paper()),
          Lizard().compete(Scissors()),
          Lizard().compete(Rock()),
          Lizard().compete(Lizard()))
#: win win lose draw
```

This version costs far more to extend. Every existing class
(`Paper`, `Scissors`, `Rock`) needs a new `eval_lizard()` method.
The `__main__` guard serves exercise 3, as in exercise 1. The new `Lizard` class needs a `compete()` plus four
`eval_*()` methods, one per opponent type including its own. Those
methods encode the same sixteen answers already sitting in the table
version's `OUTCOME` dictionary, spread across four classes instead of
collected in one place. The two implementations agree on all sixteen
combinations.

The comparison makes the chapter's point concrete. The table costs one
class and seven dictionary rows to extend. The method version costs
one class and five new methods, plus retrofitting a method onto every
class that already exists. That cost only grows as you add more item
types. The chapter therefore recommends the table by default, and
reserves the method version for behavior that belongs to the class: a
combination that reads the object's own state, or one a subclass
should override while inheriting the rest.

## 3. Sixteen matchups in `EXPECTED`

> In `test_paper_scissors.py`, add `Lizard`'s seven matchups to `EXPECTED`,
> taking it from nine entries to sixteen,
> and confirm both versions still agree with each other and with `EXPECTED`.

```python
# exercise_3.py
from types import ModuleType
from typing import Final
import exercise_1 as table
import exercise_2 as methods
from exercise_1 import Outcome

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

def compete(module: ModuleType, player: str,
            opponent: str) -> str:
    return getattr(module, player)().compete(
        getattr(module, opponent)())

for module in (table, methods):
    wrong = [pair for pair, result in EXPECTED.items()
             if compete(module, *pair) != result]
    print(module.__name__, len(EXPECTED), "agree:",
          not wrong)
#: exercise_1 16 agree: True
#: exercise_2 16 agree: True
```

The two modules are exercise 1's table and exercise 2's methods, the
two versions that know `Lizard`. `compete()` is the test's helper:
it looks each class up by name on whichever module it receives, so one
`EXPECTED` drives both sets of classes. Each module defines its own
`Outcome`, and the comparison still works, since a `StrEnum` member
equals its string value.

In `test_paper_scissors.py`, the sixteen-entry `EXPECTED` is the one
change to the test, once its two imports name modules that include
`Lizard`. `test_matches_expected()` hardcodes no
number of item types. `pytest` parametrizes it from `MATCHUPS`, which a
comprehension builds from `EXPECTED`, so the test reports sixteen
cases per module where it reported nine.

## 4. Counting how often each item type appears

> In `arena.py`, give `item_pair_gen()` an optional `counts: Counter[str] | None = None` parameter,
> and have it update that counter in place with a tally of every item type it chooses.
> It still yields `(item1, item2)` pairs, so existing calls need no change.
> The counter fills only as you consume the generator,
> so pass in your own `Counter`,
> iterate over all 100 pairs from `item_pair_gen(Item, 100, counts)`,
> and then print how many times `Lizard` appeared.

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

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
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
```

`counts` is an optional parameter with a default of `None`, so every
existing call such as `item_pair_gen(Item, 10)` still works exactly as
before, unpacking a plain `(item1, item2)` pair each time. Only a
caller that wants the tally needs to pass its own `Counter` in. The
generator then updates that same object in place on every pair it
produces, one increment per item, so the caller can read
`counts["Lizard"]` at any point during or after the loop, without
`item_pair_gen()` needing to change what it yields.

## 5. `__sub__()` and `__rsub__()` on `Meters`

> Give `Meters` a `__sub__()` and a `__rsub__()`.
> `__sub__()` handles a `Meters`, an `int`, or a `float`,
> and returns `NotImplemented` for anything else.
> `__rsub__()` needs only the `int` and `float` cases,
> since Python never calls the reflected form for two `Meters`.
> Subtraction does not commute, so the reflected form must undo the swap:
> check that `10 - Meters(3)` produces `Meters(7)` rather than `Meters(-7)`.
> Then confirm that `"ten" - Meters(3)` raises a `TypeError` rather than producing a `Meters`.

```python
# exercise_5.py
from exceptions import expected
from record import record

@record
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
            # Not self.n - other
            return Meters(other - self.n)
        return NotImplemented

print(Meters(10) - Meters(3), Meters(10) - 3)
#: Meters(n=7) Meters(n=7)
print(10 - Meters(3))
#: Meters(n=7)
with expected(TypeError):
    "ten" - Meters(3)
#: [TypeError] unsupported operand type(s) for -: 'str' and
#: 'Meters'
```

`__sub__()` is `__add__()` with the sign changed, and the three cases
line up the same way: a `Meters`, a number, or `NotImplemented` for
anything else. `__rsub__()` needs only the numeric case, because
Python asks the left operand first, and `Meters.__sub__()` already
answers `Meters(10) - Meters(3)`. Python tries the reflected form only
when the left operand declines, and two `Meters` never decline.

The swap is where subtraction differs from addition. Python calls
`Meters.__rsub__(Meters(3), 10)` for the expression `10 - Meters(3)`,
so `self` is the right operand and `other` is the left one. The method
must put them back in the order the source wrote them.
`Meters(other - self.n)` gives `Meters(7)`. Writing
`Meters(self.n - other)`, the same body `__sub__()` uses, gives
`Meters(-7)`: a correct-looking method that quietly returns the
negative of every reflected subtraction. `__radd__()` hides that swap
because addition commutes, so the mistake costs nothing there and
costs the wrong answer here.

`"ten" - Meters(3)` finds no `str.__sub__` at all, so Python goes
straight to `Meters.__rsub__`, which returns `NotImplemented` for a
`str`. With both sides declining, Python raises the `TypeError`, and
the message names both types. Returning `NotImplemented` rather than
raising an exception makes that message possible: an exception raised
inside `__rsub__()` reports `Meters`'s complaint instead of
Python's account of which pair of types has no defined subtraction.

## 6. Making the table tolerate subclasses

> Subclass `Paper` as `Origami` and duel it against `Rock` in the table version,
> as `exact_match.py` does.
> Explain the `KeyError` in terms of how the lookup matches.
> Then make the table match subclasses by walking both operands' `__mro__` for the first pair that has a row,
> and say what becomes of each of the two properties the lookup shares with the table-driven state machine.

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

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
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
equality. `Origami` inherits from `Paper` but is not `Paper`, so
`(Origami, Rock)` is not `(Paper, Rock)`. Inheritance never enters the
lookup: a `dict` hashes the key and compares, and neither step
consults an MRO. That is what the chapter's "matches classes exactly"
means, and exact matching is the property `singledispatch` does not
share.

The tolerant version walks both MROs and takes the first pair that has
a row, so `TolerantOrigami` finds `(TolerantPaper, TolerantRock)` one
step up on the left. What that version gives up is exactly the
property the chapter names first: the match is no longer exact. Three
consequences follow, and only the first is obvious.

The lookup is no longer one probe. It is a nested loop over two MROs,
so a miss now costs the product of the two depths instead of a single
hash. For a table consulted once per duel, that cost vanishes into the
noise. In an inner loop, it matters.

Order now decides the answer. `(TolerantPaper, TolerantRock)` and
`(TolerantOrigami, TolerantItem)` could both match. Which one wins
depends on the order the loops happen to walk, not on anything a
reader of the table can see. The exact version has no such question:
either the pair is in the table or it is not.

The tolerant version also loses the failure that makes the exact
version safe, though only for a subclass of a concrete item. An
`Origami(Paper)` whose rows you forgot to write no longer raises a
`KeyError`. It silently inherits `Paper`'s answers and plays as paper.
A `Lizard(Item)` still fails fast, since no row has `Item` in its key
and the MRO walk finds nothing to inherit. Tolerance buys the
convenience of skipping rows at the price of the fail-fast policy the
chapter recommends for a table under construction, and it buys it
exactly where the table is most likely to mistake a new type for an
old one.

Which behavior you want depends on whether a subclass is a new
competitor or a variation on an existing one. `Origami` really is
paper for the purposes of this game. A `WetPaper` that loses to
everything is a new competitor.

## 7. A business-modeling environment

> Create a business-modeling environment with three types of `Inhabitant`:
> `Dwarf` (for engineers), `Elf` (for marketers), and `Troll` (for managers).
> Now create a class called `Project` that creates the different inhabitants and causes them to `interact()` with each other.
> Single dispatch is enough here.
> The next exercise adds the second dispatch.

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

    def meet(self, n: int) -> None:
        team = self.gather(n)
        for a, b in zip(team, team[1:]):
            print(a.interact(b))

Project(seed=1).meet(4)
#: Dwarf (engineer) negotiates with Troll
#: Troll (manager) directs Dwarf
#: Dwarf (engineer) negotiates with Elf
```

`Project` creates the inhabitants in `gather()` and makes neighbors
interact in `meet()`. Exercise 7 uses single dispatch, not double:
`a.interact(b)` resolves on `a`'s type only, and `interact()`
interpolates `other` without inspecting its type. The design becomes
double dispatch once `interact()`'s behavior must vary by `other`'s type too,
and exercise 8 adds that dependence.

## 8. Weapons, battles, and a full meeting

> Modify the previous exercise's `Project` to make the interactions more detailed.
> Each `Inhabitant` can randomly produce a `Weapon` using `get_weapon()`:
> a `Dwarf` uses `Jargon` or `Play`,
> an `Elf` uses `InventFeature` or `SellImaginaryProduct`,
> and a `Troll` uses `Edict` or `Schedule`.
> You must decide which weapons "win" and "lose" in each interaction
> (as in `paper_scissors_rock.py`).
> Add a `battle()` method to `Project` that takes two `Inhabitant`s and matches them against each other.
> Now create a `meeting()` method for `Project` that creates groups of `Dwarf`,
> `Elf`, and `Troll` and battles the groups against each other until only members of one group remain.
> These are the "winners."

The listing gives each `Inhabitant` kind two of six weapon types,
ranked around a cycle: each weapon beats the previous two in the
ranking and loses to the next two. Six is an even number, so one pair
remains. Each weapon has an opposite, three steps around the circle,
which it neither beats nor loses to, and that pair draws.
`paper_scissors_rock.py` needs no such case because three items leave
nothing over: with an odd count every weapon beats half the rest and
loses to the other half. An even count always leaves the opposite pair
to define.

```python
# exercise_8.py
import random
from enum import StrEnum
from typing import Any, ClassVar, override

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Weapon:
    def compete(self, item: Any) -> Outcome:
        raise NotImplementedError
    def __str__(self) -> str:
        return type(self).__name__

class Jargon(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_jargon(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.LOSE

class Play(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_play(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.WIN
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.LOSE

class InventFeature(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_invent_feature(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.WIN
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.DRAW

class SellImaginaryProduct(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_sell_imaginary_product(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.WIN

class Edict(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_edict(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.WIN

class Schedule(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_schedule(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.DRAW

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> Weapon:
        return self.rng.choice(self.WEAPONS)()

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = a.get_weapon().compete(b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2,
                 "Troll": Troll2}
        groups = {
            name: [cls(self.rng) for _ in range(group_size)]
            for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(
                        groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

if __name__ == "__main__":
    print(Play().compete(Jargon()),
          Jargon().compete(Play()),
          Jargon().compete(SellImaginaryProduct()))
    print(Project2(seed=3).meeting(group_size=5))
#: win lose draw
#: Troll
```

`battle()` starts the two dispatches.
`a.get_weapon().compete(...)` resolves the first weapon's type,
and that class's `compete()` calls the `eval_*()` method named for it on the second weapon,
which resolves the second type.
As in `paper_scissors_rock.py`,
each `eval_*()` method answers for the caller its name identifies,
so `Jargon.eval_play()` returns `WIN` because play beats jargon.
`Weapon` declares `compete()` so that `battle()` can call it on the `Weapon` that `get_weapon()` returns.
The `eval_*()` methods stay undeclared,
and their `item` parameters take `Any`, as the chapter's do.

Six weapons take 42 methods,
a `compete()` and six `eval_*()` methods in each class,
and more than a hundred lines hold 36 answers.
That length is the cost
[Methods or Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#methods-or-table)
weighs, at four times the chapter's nine answers.
The answers grow with the square of the number of weapons.
A seventh weapon would add an `eval_*()` method to each of the six classes,
plus a new class of eight methods.
Exercise 10 collects the same 36 answers in one place.

The weapon ranking is a genuine cycle: nothing dominates everything,
so no group can count on winning. At the group level the same cycle
appears one level up. An `Elf` beats a `Dwarf` on three of their four
weapon pairings, a `Troll` beats an `Elf` on three of four, and a
`Dwarf` beats a `Troll` on three of four, with the fourth pairing in
each case the draw. Over two hundred seeds all three kinds win
`meeting(5)`, so the outcome depends on the random draws each round,
exactly as it does in a real rock-paper-scissors tournament.

## 9. A table of callables

> The chapter claims that a table cell can hold a function,
> so even elaborate behavior fits the table.
> Build that version.
> In `paper_scissors_rock_table.py`,
> give every `OUTCOME` cell a `Callable[[Item, Item], Outcome]` in place of its `Outcome`,
> and have `compete()` call the cell it finds:
> `OUTCOME[type(self), type(item)](self, item)`.
> The call site stays `item1.compete(item2)`.
> Write a helper that wraps a constant `Outcome` in a callable,
> so the seven unchanged cells stay one line each.
> Then give `Paper` a `wet` attribute and make the `(Paper, Rock)` and `(Rock, Paper)` cells read it:
> dry paper wraps the rock and wins, wet paper is too soggy and draws,
> whichever of the two calls `compete()`.
> The chapter gives two reasons for preferring the double-dispatch version.
> Say which one this change answers, and which one survives it.

```python
# exercise_9.py
from collections.abc import Callable
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, item: Item) -> Outcome:
        return OUTCOME[type(self), type(item)](self, item)
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def __init__(self, wet: bool = False) -> None:
        self.wet = wet
    def __str__(self) -> str:
        return "WetPaper" if self.wet else "Paper"

class Scissors(Item):
    pass
class Rock(Item):
    pass

type Cell = Callable[[Item, Item], Outcome]

def always(outcome: Outcome) -> Cell:
    return lambda item1, item2: outcome

def paper_vs_rock(item1: Item, item2: Item) -> Outcome:
    if isinstance(item1, Paper) and item1.wet:
        return Outcome.DRAW  # Too soggy to wrap a rock
    return Outcome.WIN

def rock_vs_paper(item1: Item, item2: Item) -> Outcome:
    if isinstance(item2, Paper) and item2.wet:
        return Outcome.DRAW  # The same soggy draw
    return Outcome.LOSE

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Cell]] = {
    (Paper, Rock): paper_vs_rock,
    (Paper, Scissors): always(Outcome.LOSE),
    (Paper, Paper): always(Outcome.DRAW),
    (Scissors, Paper): always(Outcome.WIN),
    (Scissors, Rock): always(Outcome.LOSE),
    (Scissors, Scissors): always(Outcome.DRAW),
    (Rock, Scissors): always(Outcome.WIN),
    (Rock, Paper): rock_vs_paper,
    (Rock, Rock): always(Outcome.DRAW),
}

for item1, item2 in [
    (Paper(), Rock()),
    (Paper(wet=True), Rock()),
    (Rock(), Paper(wet=True)),
    (Scissors(), Paper()),
    (Rock(), Rock()),
]:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
#: Paper <--> Rock : win
#: WetPaper <--> Rock : draw
#: Rock <--> WetPaper : draw
#: Scissors <--> Paper : win
#: Rock <--> Rock : draw
```

`compete()` changes by one pair of parentheses. It still finds the
cell with a single probe keyed on both types, and now calls what it
finds instead of returning it. The call site never learns any of
this: `item1.compete(item2)` reads as it does in
`paper_scissors_rock.py`, where four method definitions per class
stand behind it. A table of callables keeps the method-call syntax.

`always()` is what keeps the table readable. It returns a closure
over one `Outcome` that ignores both operands, so the seven
combinations with a fixed answer stay one line each and still read as
a table of answers. Only the cells that need code look like code.

The `(Paper, Rock)` cell receives both items, so it can consult
`item1.wet`. The `(Rock, Paper)` cell consults `item2.wet`, because
one duel has two orders and each order has its own cell. Without it,
a rock that calls `compete()` would still beat wet paper. That is the
first of the two reasons the chapter gives for preferring the
double-dispatch version: behavior that reads the object's own state. A cell holding a function answers it. Whatever
`Paper.eval_rock()` can read, `paper_vs_rock()` can read too,
from the same two objects.

The second reason survives. A subclass still cannot override one
combination and inherit the rest, because the lookup still matches
types exactly: an `Origami(Paper)` finds no row at all, callable or
not, and the fix is to write `Origami`'s rows rather than to override
one. Changing a cell changes it for every `Item`, since `OUTCOME` is
one shared dictionary. `paper_scissors_rock_subclass.py`'s `DampPaper`
gets its exception by overriding `compete()` and `eval_rock()`, and
this version has nothing to override: `Item` defines `compete()` once.

One cost comes with the change. `paper_vs_rock()` and
`rock_vs_paper()` take two `Item`s, because every cell must, so each
recovers `Paper` with an `isinstance()` test. That is the type test
the chapter warns about in the ladder version, and here it sits inside
one cell rather than
running through every class, which is the difference between a test
you write once and a test every new `Item` forces you to edit.

## 10. Exercise 8, rebuilt on a table

> Modify exercise 8 to use the table lookup technique of `paper_scissors_rock_table.py`.

```python
# exercise_10.py
import random
from typing import ClassVar, Final
import exercise_8 as methods
from exercise_8 import Outcome

class Weapon:
    def compete(self, item: Weapon) -> Outcome:
        return OUTCOME[type(self), type(item)]
    def __str__(self) -> str:
        return type(self).__name__

class Jargon(Weapon):
    pass
class Play(Weapon):
    pass
class InventFeature(Weapon):
    pass
class SellImaginaryProduct(Weapon):
    pass
class Edict(Weapon):
    pass
class Schedule(Weapon):
    pass

type Table = dict[
    tuple[type[Weapon], type[Weapon]], Outcome]

W: Final[Outcome] = Outcome.WIN
L: Final[Outcome] = Outcome.LOSE
D: Final[Outcome] = Outcome.DRAW
ORDER: Final[tuple[type[Weapon], ...]] = (
    Jargon, Play, InventFeature,
    SellImaginaryProduct, Edict, Schedule)
GRID: Final[tuple[tuple[Outcome, ...], ...]] = (
    (D, L, L, D, W, W),  # Jargon
    (W, D, L, L, D, W),  # Play
    (W, W, D, L, L, D),  # InventFeature
    (D, W, W, D, L, L),  # SellImaginaryProduct
    (L, D, W, W, D, L),  # Edict
    (L, L, D, W, W, D),  # Schedule
)
OUTCOME: Final[Table] = {
    (a, b): cell
    for a, row in zip(ORDER, GRID, strict=True)
    for b, cell in zip(ORDER, row, strict=True)
}

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> Weapon:
        return self.rng.choice(self.WEAPONS)()

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = a.get_weapon().compete(b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2,
                 "Troll": Troll2}
        groups = {
            name: [cls(self.rng) for _ in range(group_size)]
            for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(
                        groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

def by_methods(a: type[Weapon],
               b: type[Weapon]) -> Outcome:
    return getattr(methods, a.__name__)().compete(
        getattr(methods, b.__name__)())

wrong = [pair for pair, result in OUTCOME.items()
         if by_methods(*pair) != result]
print(len(OUTCOME), "pairs agree with exercise 8:",
      not wrong)
#: 36 pairs agree with exercise 8: True
print(Project2(seed=3).meeting(group_size=5))
#: Troll
```

The weapons shrink to six empty classes,
and `Weapon.compete()` makes one lookup keyed on both types,
as in `paper_scissors_rock_table.py`.
The listing writes the 36 answers by hand,
as a grid rather than as 36 dictionary rows.
Each row of `GRID` holds one weapon's results as the caller,
against the weapons in `ORDER`,
and the comprehension turns the grid into the `(caller, opponent)` keys that `compete()` looks up.
A cell holds what one of exercise 8's `eval_*()` methods returns:
row `Jargon`, column `Play`, holds the `LOSE` that `Play.eval_jargon()` returns.
`by_methods()` plays each pair through exercise 8's classes,
finding them by name as exercise 3 does,
and all 36 answers agree.
`Troll2`, `battle()`, and `meeting()` repeat exercise 8's code,
so the seeded meeting draws the same weapons and `Troll` wins again.

The grid holds in six lines the answers that exercise 8 spreads across 42 methods.
A seventh weapon adds an empty class, a row, and a column,
where exercise 8 needs a method in every existing class and an eight-method class.
[Methods or Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#methods-or-table)
reaches the same conclusion: for a ruleset that is a fixed set of
answers, the table is shorter and easier to maintain.
Exercise 8's version keeps one advantage.
Its `eval_*()` methods receive the competing objects,
so a weapon whose result depends on its own state fits there,
while this grid would need exercise 9's callable cells.
