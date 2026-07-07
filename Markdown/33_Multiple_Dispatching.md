# Multiple Dispatching

Dealing with multiple interacting types can get messy.
Consider a system that parses and executes mathematical expressions.
You want to say `Number + Number`, `Number * Number`, etc.,
where `Number` is the base class for a family of numerical objects.
But when you say `a + b`,
and you don't know the exact type of either `a` or `b`,
how can you get them to interact properly?

The answer starts with something you probably never consider.
Python only performs single dispatching.
That is, if you are performing an operation on more than one object whose type is unknown,
Python can invoke the dynamic binding mechanism on only one of those types.
You end up detecting some types manually and effectively producing your own dynamic binding behavior.

The solution is *Multiple Dispatching*.
Polymorphism broadly means that a function accepts arguments of more than one type
(see [Rethinking Objects](21_Rethinking_Objects.md#polymorphism-without-inheritance)).
It takes several forms.
Function overloading in C++ picks a function from the argument types.
Generics write one body that works across many types.
The form at work in this chapter is the runtime dispatch that inheritance provides,
which resolves on the type of one object, the one receiving the method call.
That is why one method call can resolve only one unknown type.

To dispatch on two unknown types, you need two method calls.
The first resolves the first type, and the second resolves the second.
Each unknown type needs its own dispatching method call.
The following example names its methods `compete()` and `eval_*()`,
and all belong to the same hierarchy.
Here there will be only two dispatches; this is *double dispatching*.
If you are working with two different type hierarchies that are interacting,
then you'll need a dispatching method call for each hierarchy.

Both versions below share one result type, an enumeration called `Outcome`:
either `WIN`, `LOSE`, or `DRAW`.
`Outcome` is a `StrEnum`, so each member is its string value and prints as `win`,
`lose`, or `draw`:

```python
# outcome.py
# The result of one Item competing with another.
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
```

We also need two small helper functions,
one to generate random pairs of items,
and one to play a pair off and print the result:

```python
# arena.py
import random
from collections.abc import Iterator
from typing import Any

# Seed for reproducibility
random.seed(47)

def item_pair_gen(base: type, n: int) -> Iterator[tuple[Any, Any]]:
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()

def duel(item1: Any, item2: Any) -> None:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
```

Here we demonstrate *Multiple Dispatching*:

```python
# paper_scissors_rock.py
from typing import Any
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper, we're in Paper
        return Outcome.DRAW
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors, we're in Paper
        return Outcome.WIN
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock, we're in Paper
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper, we're in Scissors
        return Outcome.LOSE
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors, we're in Scissors
        return Outcome.DRAW
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock, we're in Scissors
        return Outcome.WIN

class Rock(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Item was Paper, we're in Rock
        return Outcome.WIN
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors, we're in Rock
        return Outcome.LOSE
    def eval_rock(self, item: Any) -> Outcome:
        # Item was Rock, we're in Rock
        return Outcome.DRAW

if __name__ == "__main__":
    for item1, item2 in item_pair_gen(Item, 10):
        duel(item1, item2)
#: Scissors <--> Paper : win
#: Scissors <--> Rock : lose
#: Scissors <--> Rock : lose
#: Scissors <--> Scissors : draw
#: Rock <--> Scissors : win
#: Scissors <--> Rock : lose
#: Paper <--> Scissors : lose
#: Rock <--> Paper : lose
#: Paper <--> Paper : draw
#: Scissors <--> Scissors : draw
```

Each type of `Item` encodes the information about the various combinations.
This is a kind of table, spread across the classes.
It is not easy to maintain if you expect to modify the behavior or to add a new `Item` class.
It can be more sensible to make the table explicit, like this:

```python
# paper_scissors_rock_table.py
from typing import Any, Final
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def compete(self, item: Any) -> Outcome:
        # Use a tuple of types to index into the table:
        return OUTCOME[self.__class__, item.__class__]
    def __str__(self) -> str:
        return self.__class__.__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

OUTCOME: Final[dict[tuple[type, type], Outcome]] = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
}

if __name__ == "__main__":
    for item1, item2 in item_pair_gen(Item, 10):
        duel(item1, item2)
#: Scissors <--> Paper : win
#: Scissors <--> Rock : lose
#: Scissors <--> Rock : lose
#: Scissors <--> Scissors : draw
#: Rock <--> Scissors : win
#: Scissors <--> Rock : lose
#: Paper <--> Scissors : lose
#: Rock <--> Paper : lose
#: Paper <--> Paper : draw
#: Scissors <--> Scissors : draw
```

Notice the flexibility of dictionaries. A tuple serves as a key just as easily as a single object.

## One Type or Many

Python dispatches on a single type at a time.
For dispatch on one argument's type,
`functools.singledispatch` (see [Visitor](34_Visitor.md#the-pythonic-visitor-singledispatch)) gives you open,
per-type functions.
For dispatch on two or more types at once,
the table above is the idiomatic answer: a `dict` keyed by a tuple of types.
Adding a new `Item` is then a matter of adding rows to the table,
with no methods to edit across the classes.

The double-dispatch version, where each class implements `eval_paper()`,
`eval_scissors()`, and `eval_rock()`,
is a workaround for languages that cannot store types in a table and look a behavior up by them.
Python can, so the table is both shorter and easier to maintain.
Use the spread-out method version only when a combination needs substantial,
type-specific code that will not fit in a table cell.

The win/lose/draw result is pure logic,
which makes it easy to validate through testing.
The spread-out method version and the table version must return the same `Outcome` for every one of the nine combinations.
If they diverge, one of them has a bug.

```python
# test_paper_scissors.py
from typing import Any, Final
import paper_scissors_rock as methods
import paper_scissors_rock_table as table
from outcome import Outcome

# (player, opponent): the player's result
EXPECTED: Final[dict[tuple[str, str], Outcome]] = {
    ("Paper", "Rock"): Outcome.WIN,
    ("Paper", "Scissors"): Outcome.LOSE,
    ("Paper", "Paper"): Outcome.DRAW,
    ("Scissors", "Paper"): Outcome.WIN,
    ("Scissors", "Rock"): Outcome.LOSE,
    ("Scissors", "Scissors"): Outcome.DRAW,
    ("Rock", "Scissors"): Outcome.WIN,
    ("Rock", "Paper"): Outcome.LOSE,
    ("Rock", "Rock"): Outcome.DRAW,
}

def compete(module: Any, player: str, opponent: str) -> Outcome:
    result = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

def test_table_version_matches_expected() -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(table, player, opponent) == result

def test_method_version_matches_expected() -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(methods, player, opponent) == result

def test_both_versions_agree() -> None:
    for player, opponent in EXPECTED:
        assert (compete(methods, player, opponent)
                == compete(table, player, opponent))

def test_outcome_str() -> None:
    assert str(Outcome.WIN) == "win"
    assert str(Outcome.LOSE) == "lose"
    assert str(Outcome.DRAW) == "draw"
```

Importing both modules works cleanly because each guards its demonstration loop with `if __name__ == "__main__"`,
so the loop runs only when you execute the file directly,
not when a test imports it.

## Exercises

1.  Add a fourth `Item`, `Lizard`, to `paper_scissors_rock_table.py`.
    Lizard beats Paper and Scissors, and loses to Rock;
    Lizard versus Lizard is a draw.
    Add the six new entries (both orders of every pair) that `OUTCOME` needs.
2.  Add the same `Lizard` to `paper_scissors_rock.py`, the double-dispatch version,
    which means adding an `eval_lizard()` method to every existing class,
    plus a `Lizard` class with its own `compete()` and four `eval_*()` methods.
    Compare how much code this took versus adding `Lizard` to the table version.
3.  In `test_paper_scissors.py`, add `Lizard` to `EXPECTED` with its nine (now sixteen)
    matchups, and confirm both versions still agree with each other and with `EXPECTED`.
4.  In `arena.py`, give `item_pair_gen()` an optional `counts: Counter[str] | None = None`
    parameter that it updates in place with a tally of every item type it chooses,
    while still yielding plain `(item1, item2)` pairs so existing calls need no change.
    Pass in your own `Counter` and print how many times `Lizard` appeared across
    `item_pair_gen(Item, 100, counts)`.
