# Multiple Dispatching

When dealing with multiple types which are interacting,
a program can get particularly messy.
For example, consider a system that parses and executes mathematical expressions.
You want to  say `Number + Number`, `Number \* Number`, etc.,
where `Number` is the base class for a family of numerical objects.
But when you say `a + b`,
and you don't know the exact type of either `a` or `b`,
how can you get them to interact properly?

The answer starts with something you probably don't think about:
Python performs only single dispatching.
That is, if you are performing an operation on more than one object whose type is unknown,
Python can invoke the dynamic binding mechanism on only one of those types.
This doesn't solve the problem,
so you end up detecting some types manually and effectively producing your own dynamic binding behavior.

The solution is called *Multiple Dispatching*.
Remember that polymorphism can occur only via method calls,
so if you want double dispatching to occur, there must be two method calls:
the first to determine the first unknown type,
and the second to determine the second unknown type.
With *Multiple Dispatching*,
you must have a polymorphic method call to determine each of the types.
The methods in the following example are called `compete()` and `eval()`,
and are both members of the same type.
(Here there will be only two dispatches, which is referred to as *double dispatching*).
If you are working with two different type hierarchies that are interacting,
then you'll have to have a polymorphic method call in each hierarchy.

Both versions below share one result type: an enumeration of the three outcomes,
win, lose, and draw.
Rather than duplicate it, put it in its own module for import.
It is a `StrEnum`, so each member is its string value and prints as `win`,
`lose`, or `draw` with no extra code:

```python
# outcome.py
# The win/lose/draw result of one Item competing with another.
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
```

Both versions also share two small helpers:
one to generate random pairs of items,
and one to play a pair off and print the result.
Those go in a module too,
so each example below shows only its dispatch mechanism:

```python
# arena.py
import random
from collections.abc import Iterator
from typing import Any

# Seed once so the matchups are reproducible across the chapter
random.seed(47)

def item_pair_gen(base: type, n: int) -> Iterator[tuple[Any, Any]]:
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()

def match(item1: Any, item2: Any) -> None:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
```

Here's an example of *Multiple Dispatching*:

```python
# paper_scissors_rock.py
# Demonstration of multiple dispatching.
from typing import Any
from arena import item_pair_gen, match
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
    for item1, item2 in item_pair_gen(Item, 20):
        match(item1, item2)
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
#: Rock <--> Rock : draw
#: Paper <--> Scissors : lose
#: Rock <--> Scissors : win
#: Paper <--> Paper : draw
#: Rock <--> Rock : draw
#: Scissors <--> Scissors : draw
#: Paper <--> Paper : draw
#: Rock <--> Scissors : win
#: Rock <--> Rock : draw
#: Scissors <--> Rock : lose
```

One of the things you might notice is that the information about the various combinations is encoded into each type of `Item`.
It actually ends up being a kind of table,
except that it is spread out through all the classes.
This is not easy to maintain if you expect to modify the behavior or to add a new `Item` class.
Instead, it can be more sensible to make the table explicit, like this:

```python
# paper_scissors_rock2.py
# Multiple dispatching using a table
from typing import Any, Final
from arena import item_pair_gen, match
from outcome import Outcome

class Item:
    def compete(self, item: Any) -> Outcome:
        # Use a tuple for table lookup:
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
    for item1, item2 in item_pair_gen(Item, 20):
        match(item1, item2)
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
#: Rock <--> Rock : draw
#: Paper <--> Scissors : lose
#: Rock <--> Scissors : win
#: Paper <--> Paper : draw
#: Rock <--> Rock : draw
#: Scissors <--> Scissors : draw
#: Paper <--> Paper : draw
#: Rock <--> Scissors : win
#: Rock <--> Rock : draw
#: Scissors <--> Rock : lose
```

Notice the flexibility of dictionaries: a tuple can be used as a key just as easily as a single object.

## One Type or Many

Python dispatches on a single type at a time.
For dispatch on *one* argument's type,
`functools.singledispatch` (see [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch)) gives you open,
per-type functions.
For dispatch on *two or more* types at once,
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
which makes it easy to pin down with a test.
The strongest check is that the two versions agree:
the spread-out method version and the table version must return the same `Outcome` for every one of the nine combinations.
If they ever diverge, one of them has a bug.

```python
# test_paper_scissors.py
from typing import Any, Final
import paper_scissors_rock as methods
import paper_scissors_rock2 as table
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
so the loop runs only when the file is executed directly,
not when it is imported for testing.
