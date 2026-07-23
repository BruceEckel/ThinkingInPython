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
(see [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance)).
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
Here there will be only two dispatches.
This is *double dispatching*.
If you are working with two different type hierarchies that are interacting,
then you'll need a dispatching method call for each hierarchy.

Both versions below share one result type, an enumeration called `Outcome`:
either `WIN`, `LOSE`, or `DRAW`.
`Outcome` is a `StrEnum`,
so each member is its string value and prints as `win`, `lose`, or `draw`:

```python
# outcome.py
# The result of one Item competing with another.
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
```

We also need two small helper functions, one to generate random pairs of items,
and one to play a pair off and print the result:

```python
# arena.py
import random
from collections.abc import Iterator
from typing import Any

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
import random
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
    random.seed(47)  # Reproducible pairs
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

![Scissors.compete(paper) calls item.eval_scissors(self); self and item swap sides on the second call, landing execution inside Paper.eval_scissors() rather than Scissors's own code](_images/double_dispatch)

Follow one duel to keep the perspective straight.
`scissors.compete(paper)` resolves `self` to `Scissors`, the first dispatch,
and calls `paper.eval_scissors(...)`.
That call is the second dispatch: it resolves `paper`,
landing in `Paper.eval_scissors()`, the one method that knows both types.
Now note whose result it returns.
`Paper.eval_scissors()` returns `WIN`,
and that is the outcome for the *scissors that started the duel*,
not for the `Paper` whose code is running: scissors cut paper.
Every `eval_*()` method answers for the original caller,
the object named in the method's own name.
Misread that convention and every result in the class appears backward.

Each type of `Item` encodes the information about the various combinations.
This is a kind of table, spread across the classes.
It is not easy to maintain if you expect to modify the behavior or to add a new `Item` class.
It can be more sensible to make the table explicit, like this:

```python
# paper_scissors_rock_table.py
import random
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
    random.seed(47)  # Reproducible pairs
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

Notice the flexibility of dictionaries.
A tuple serves as a key just as easily as a single object.
Two properties of the lookup carry over from the [table-driven state machine](31_State_Machines.md#the-engine).
The match is on classes *exactly*,
so a subclass of `Paper` finds none of `Paper`'s rows.
And a missing pair raises `KeyError` at the first duel that needs it,
the fail-fast policy that suits a table under construction,
which is exactly what you want while adding `Lizard` in exercise 1.

## One Type or Many

Python dispatches on a single type at a time.
For dispatch on one argument's type, `functools.singledispatch`
(see [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch))
gives you open, per-type functions.
For dispatch on two or more types at once,
the table above is the idiomatic answer: a `dict` keyed by a tuple of types.
Adding a new `Item` is then a matter of adding rows to the table,
with no methods to edit across the classes.

The version most programmers write first is neither of these:
it is an `isinstance()` ladder inside `compete()`,
testing the opponent's type case by case.
It works, and it is the worst of both worlds,
type tests scattered through every class like the method version,
with none of dispatch's automatic resolution,
and every new `Item` forces an edit to every ladder.
Both patterns in this chapter exist to avoid writing it.

The double-dispatch version, where each class implements `eval_paper()`,
`eval_scissors()`, and `eval_rock()`,
is a workaround for languages that cannot store types in a table and look a behavior up by them.
Python can, so the table is both shorter and easier to maintain.
Use the spread-out method version only when a combination needs substantial,
type-specific code that will not fit in a table cell.

Python's own operators already contain a two-step dispatch,
and it answers the `Number + Number` question that opened this chapter.
`a + b` first tries `type(a).__add__(a, b)`.
If that returns the special value `NotImplemented`,
Python turns around and tries `type(b).__radd__(b, a)`.
The first call dispatches on `a`'s type, the fallback on `b`'s:
double dispatching, built into the language.
This is how an `int` on the left can learn to add itself to a type written decades after `int` was.
Returning `NotImplemented`
(a sentinel value, not the `NotImplementedError` exception, a lookalike pair worth keeping apart)
is how an operand says "I don't know this type; ask the other object."
Here is the machinery, with each dispatch traced:

```python
# radd_dispatch.py
from typing import Any

class Meters:
    def __init__(self, n: float) -> None:
        self.n = n

    def __repr__(self) -> str:
        return f"Meters({self.n})"

    def __add__(self, other: object) -> Any:
        print(f"__add__({self!r}, {other!r})")
        if isinstance(other, Meters):
            return Meters(self.n + other.n)
        if isinstance(other, int | float):
            return Meters(self.n + other)
        return NotImplemented

    def __radd__(self, other: object) -> Any:
        print(f"__radd__({self!r}, {other!r})")
        if isinstance(other, int | float):
            return Meters(other + self.n)
        return NotImplemented

print(Meters(3) + Meters(4))
#: __add__(Meters(3), Meters(4))
#: Meters(7)
print(Meters(3) + 4)  # The left operand handles it
#: __add__(Meters(3), 4)
#: Meters(7)
print(4 + Meters(3))  # Int declines; the right operand handles it
#: __radd__(Meters(3), 4)
#: Meters(7)
try:
    Meters(3) + "four"  # Both sides decline
except TypeError as e:
    print(type(e).__name__)
#: __add__(Meters(3), 'four')
#: TypeError
```

The first two additions resolve inside `__add__()`:
the left operand recognized the type.
The third is the interesting one.
`4 + Meters(3)` asks `int.__add__` first, and `int` has never heard of `Meters`,
so it returns `NotImplemented`.
Python then, with no error anywhere, turns to `Meters.__radd__`,
whose trace line shows the operands arriving swapped.
The last case shows what the sentinel is for.
`Meters.__add__` runs, declines the string, `str` has no `__radd__` to consult,
and only after both sides have declined does Python raise `TypeError`.
Declining is not failing; the error appears only when nobody volunteers.

The win/lose/draw result is pure logic,
which makes it easy to validate through testing.
The spread-out method version and the table version must return the same `Outcome` for every one of the nine combinations.
If they diverge, one of them has a bug.

```python
# test_paper_scissors.py
from typing import Any, Final
import paper_scissors_rock as methods
import paper_scissors_rock_table as table
import pytest
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
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

@pytest.mark.parametrize("module", [table, methods])
def test_matches_expected(module: Any) -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(module, player, opponent) == result

def test_both_versions_agree() -> None:
    for player, opponent in EXPECTED:
        assert (compete(methods, player, opponent)
                == compete(table, player, opponent))

@pytest.mark.parametrize("outcome, expected", [
    (Outcome.WIN, "win"),
    (Outcome.LOSE, "lose"),
    (Outcome.DRAW, "draw"),
])
def test_outcome_str(outcome: Outcome, expected: str) -> None:
    assert str(outcome) == expected
```

Importing both modules works cleanly because each guards its demonstration loop with `if __name__ == "__main__"`,
so the loop runs only when you execute the file directly,
not when a test imports it.

## Exercises

1.  Add a fourth `Item`, `Lizard`, to `paper_scissors_rock_table.py`.
    Lizard beats Paper and Scissors, and loses to Rock.
    Lizard versus Lizard is a draw.
    Add the seven new entries that `OUTCOME` needs:
    both orders of each mixed pair, plus Lizard versus Lizard.
2.  Add the same `Lizard` to `paper_scissors_rock.py`,
    the double-dispatch version,
    which means adding an `eval_lizard()` method to every existing class,
    plus a `Lizard` class with its own `compete()` and four `eval_*()` methods.
    Compare how much code this took versus adding `Lizard` to the table version.
3.  In `test_paper_scissors.py`, add `Lizard` to `EXPECTED` with its nine
    (now sixteen) matchups,
    and confirm both versions still agree with each other and with `EXPECTED`.
4.  In `arena.py`, give `item_pair_gen()` an optional `counts: Counter[str] | None = None` parameter that it updates in place with a tally of every item type it chooses,
    while still yielding `(item1, item2)` pairs so existing calls need no change.
    Pass in your own `Counter` and print how many times `Lizard` appeared across `item_pair_gen(Item, 100, counts)`.
