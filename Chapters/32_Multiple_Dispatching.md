# Multiple Dispatching

Dealing with multiple interacting types can get messy.
Consider a system that parses and executes mathematical expressions.
You want to say `Number + Number`, `Number * Number`, etc.,
where `Number` is the base class for a family of numerical objects.
But when you say `a + b`,
and you don't know the exact type of either `a` or `b`,
how can you get them to interact properly?

The answer starts with a fact about the language that rarely comes up.
Python dispatches on one type at a time.
That is, if you are performing an operation on more than one object whose type is unknown,
Python can invoke the dynamic binding mechanism on only one of those types.
You end up testing the remaining types by hand,
writing out the dispatch the language performs for the first one.

The solution is *Multiple Dispatching*.
Polymorphism broadly means that a function accepts arguments of more than one type
(see [Rethinking Objects](20_Rethinking_Objects.md#what-is-polymorphism)).
It takes several forms.
Function overloading in C++ picks a function from the argument types.
Generics write one body that works across many types.
The form at work in this chapter is the runtime dispatch that inheritance provides,
which resolves on the type of one object, the one receiving the method call.
That is why one method call can resolve only one unknown type.

To dispatch on two unknown types, you need two method calls.
The first resolves the first type, and the second resolves the second.
The following example dispatches through methods named `compete()` and `eval_*()`,
with both of the interacting objects drawn from a single hierarchy.
Two unknown types means two dispatches, which is *double dispatching*.
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

You'll also need two small helper functions,
one to generate random pairs of items,
and one to play a pair off and print the result:

```python
# arena.py
import random
from collections.abc import Iterator
from typing import Any

def item_pair_gen[T](base: type[T], n: int) -> Iterator[tuple[T, T]]:
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()

def duel(item1: Any, item2: Any) -> None:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
```

`item_pair_gen()` is generic over whichever base class it receives.
`duel()` settles for `Any` because the two versions below define separate `Item` hierarchies,
and this file must serve both.

Here is Multiple Dispatching in action:

```python
# paper_scissors_rock.py
import random
from typing import Any
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Paper, and it draws
        return Outcome.DRAW
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it wins
        return Outcome.WIN
    def eval_rock(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Rock, and it loses
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Paper, and it loses
        return Outcome.LOSE
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it draws
        return Outcome.DRAW
    def eval_rock(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Rock, and it wins
        return Outcome.WIN

class Rock(Item):
    def compete(self, item: Any) -> Outcome:
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Paper, and it wins
        return Outcome.WIN
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it loses
        return Outcome.LOSE
    def eval_rock(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Rock, and it draws
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

![Scissors.compete(paper) calls item.eval_scissors(self); self and item swap sides on the second call, putting execution inside Paper.eval_scissors() rather than Scissors's own code](_images/double_dispatch)

Follow one duel to keep the perspective straight.
`scissors.compete(paper)` resolves `self` to `Scissors`, the first dispatch,
and calls `paper.eval_scissors(...)`.
That call is the second dispatch: it resolves `paper`,
arriving in `Paper.eval_scissors()`, the one method that knows both types.
Now note whose result it returns.
`Paper.eval_scissors()` returns `WIN`,
and that is the outcome for the scissors that started the duel,
not for the `Paper` whose code is running: scissors cut paper.
Every `eval_*()` method answers for the original caller,
the object named in the method's own name.
If you misread that convention, every result in the class appears backward.
Each `eval_*()` method also receives an `item` argument, the original caller:
the same object `compete()` held as `self` before passing it along.
This game ignores it, since the outcome depends only on the two types;
a richer game would read the caller's state through it.

Note what the `Any` annotations cost.
`Item` declares neither `compete()` nor any `eval_*()` method,
so `Any` is the only annotation available short of a `Protocol` naming all four methods.
With `Any`, a checker cannot tell you when a class is missing one of the nine answers;
the gap surfaces as an `AttributeError` during whichever duel first needs it.
A `Protocol` listing the four methods would restore the checking,
at the price of a declaration that repeats every class's method names.
The table version needs neither.
Its answers are data rather than methods,
leaving no method for a class to forget, and its one method, `compete()`,
is declared on `Item`,
so the opponent parameter can be typed `Item` rather than `Any`.

Each type of `Item` encodes the information about the various combinations.
This is a kind of table, spread across the classes.
It is not easy to maintain if you expect to modify the behavior or to add a new `Item` class.
It can be more sensible to make the table explicit, like this:

```python
# paper_scissors_rock_table.py
import random
from typing import Final
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def compete(self, item: Item) -> Outcome:
        # Use a tuple of types to index into the table:
        return OUTCOME[type(self), type(item)]
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

OUTCOME: Final[dict[tuple[type[Item], type[Item]], Outcome]] = {
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
A tuple works as a key, the same as a single object.
Two properties of the lookup carry over from the [table-driven state machine](31_State_Machines.md#the-engine).
The match is on classes exactly,
so a subclass of `Paper` finds none of `Paper`'s rows.
And a missing pair raises `KeyError` at the first duel that needs it,
the fail-fast policy that suits a table under construction;
adding `Lizard` in exercise 1 puts you in that situation.

Exact matching is the property that surprises people.
This listing shows it refusing a subclass.
`Origami` derives from `Paper` and inherits its `compete()`,
but the table has no row for it:

```python
# exact_match.py
from paper_scissors_rock_table import OUTCOME, Paper, Rock

class Origami(Paper):
    pass

print(OUTCOME[Paper, Rock])
#: win
try:
    Origami().compete(Rock())
except KeyError as e:
    missing = e.args[0]  # The tuple key that was not found
    print(type(e).__name__, [c.__name__ for c in missing])
#: KeyError ['Origami', 'Rock']
```

A dictionary probe compares keys by equality,
so `Origami` is not `Paper` however closely the two relate.
Nothing walks the MRO on the way to the answer.

## One Type or Many

For dispatch on one argument's type, `functools.singledispatch`
(see [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch))
gives you open, per-type functions.
For dispatch on two or more types at once,
the table above is the idiomatic answer: a `dict` keyed by a tuple of types.
Adding a new `Item` is then a matter of adding rows to the table,
with no methods to edit across the classes.

The two match types differently.
`singledispatch` resolves through the MRO,
so registering a base class catches every subclass,
while the table matches the class exactly.
Swapping one for the other changes which pairings the code covers,
not just how many types it considers.

`functools.singledispatchmethod` sits between them.
It dispatches once on `self` through ordinary method resolution,
then again on its first argument through `singledispatch`,
which is the pair of dispatches the `eval_*()` family hand-rolls.
Each class needs its own `@singledispatchmethod`;
registering on a shared base gives every subclass one dispatcher,
so the resolution on `self` no longer distinguishes them.
That mistake is easy to make and hard to see.
Like `singledispatch`, it matches on the MRO rather than exactly.

The version most programmers write first is neither of these:
it is an `isinstance()` ladder inside `compete()`,
testing the opponent's type case by case.
It works, and it is the worst of both worlds.
The type tests scatter through every class as in the method version,
with none of dispatch's automatic resolution,
and every new `Item` forces an edit to every ladder.
Both patterns in this chapter exist to avoid writing it.

The double-dispatch version, where each class implements `eval_paper()`,
`eval_scissors()`, and `eval_rock()`,
belongs to languages where keying a table by a pair of types is awkward enough that spreading the table across the classes wins.
Python makes the table cheap, so it is both shorter and easier to maintain.
A table cell can hold a function,
so the size of the behavior does not force the choice.
Use the double-dispatch version when the behavior for a combination belongs to the class rather than to the pairing:
when it reads the object's own state,
or when a subclass should be able to override one combination and inherit the rest.

## Testing Both Versions

The win/lose/draw result is pure logic, so tests validate it easily.
The spread-out method version and the table version must return the same `Outcome` for every one of the nine combinations.
If they diverge, one of them has a bug.

```python
# test_paper_scissors.py
from types import ModuleType
from typing import Final
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

def compete(module: ModuleType, player: str,
            opponent: str) -> Outcome:
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

MATCHUPS: Final[list[tuple[str, str, Outcome]]] = [
    (p, o, r) for (p, o), r in EXPECTED.items()
]

@pytest.mark.parametrize("module", [table, methods])
@pytest.mark.parametrize("player, opponent, expected", MATCHUPS)
def test_matches_expected(module: ModuleType, player: str,
                          opponent: str, expected: Outcome) -> None:
    assert compete(module, player, opponent) == expected

@pytest.mark.parametrize("player, opponent, expected", MATCHUPS)
def test_both_versions_agree(player: str, opponent: str,
                             expected: Outcome) -> None:
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

The test imports the two modules, not their classes.
`getattr(module, player)` looks the class up on whichever module the test received,
so one table of nine expected answers drives two independent sets of `Paper`,
`Scissors`, and `Rock` classes.
Importing both modules works cleanly because each guards its demonstration loop with `if __name__ == "__main__"`,
so the loop runs only when you execute the file directly,
not when a test imports it.

## Operators Dispatch Twice

Python's own operators already perform a two-step dispatch,
which answers the `Number + Number` question that opened this chapter.
`a + b` first tries `type(a).__add__(a, b)`.
If that returns the special value `NotImplemented`,
Python turns around and tries `type(b).__radd__(b, a)`,
the *reflected* form of `__add__()`.
The first call dispatches on `a`'s type, the fallback on `b`'s:
double dispatching, built into the language.
Every arithmetic and bitwise operator has a reflected form,
named by inserting an `r` before the operator's name: `__rsub__()`,
`__rmul__()`, `__rtruediv__()`.
This fallback is how an `int` on the left can learn to add itself to a type written decades after `int` was.
Do not confuse the reflected forms with the in-place forms,
`__iadd__()` and its siblings,
which serve `+=` and take no part in the fallback.
Returning `NotImplemented`
(a sentinel value, not the lookalike `NotImplementedError` exception)
is how an operand says "I don't know this type; ask the other object."
Here is the machinery, with each dispatch traced:

```python
# radd_dispatch.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Meters:
    n: float

    def __add__(self, other: object) -> Meters:
        print(f"__add__({self!r}, {other!r})")
        if isinstance(other, Meters):
            return Meters(self.n + other.n)
        if isinstance(other, int | float):
            return Meters(self.n + other)
        return NotImplemented

    def __radd__(self, other: object) -> Meters:
        print(f"__radd__({self!r}, {other!r})")
        if isinstance(other, int | float):
            return Meters(other + self.n)
        return NotImplemented

print(Meters(3) + Meters(4))
#: __add__(Meters(n=3), Meters(n=4))
#: Meters(n=7)
print(Meters(3) + 4)  # The left operand handles it
#: __add__(Meters(n=3), 4)
#: Meters(n=7)
print(4 + Meters(3))  # Int declines; the right operand handles it
#: __radd__(Meters(n=3), 4)
#: Meters(n=7)
try:
    Meters(3) + "four"  # Both sides decline
except TypeError as e:
    print(type(e).__name__)
#: __add__(Meters(n=3), 'four')
#: TypeError
```

The first two additions resolve inside `__add__()`:
the left operand recognized the type.
`4 + Meters(3)` asks `int.__add__()` first,
and `int` has never heard of `Meters`, so it returns `NotImplemented`.
Python then, with no error anywhere, turns to `Meters.__radd__()`,
whose trace line shows the operands arriving swapped.
The last case shows why the sentinel exists.
`Meters.__add__()` runs, declines the string,
`str` has no `__radd__()` to consult,
and only after both sides have declined does Python raise `TypeError`.

Two details of the fallback are easy to get wrong.
Raising `TypeError` inside `__add__()` is not the same as returning `NotImplemented`.
The exception propagates immediately, so the right operand never gets its turn;
only the sentinel keeps the second dispatch alive.
Python also skips the reflected call when both operands have the same type,
so `Meters + Meters` settles inside `__add__()`.
A class that implements only `__radd__()` cannot add itself to its own kind.
One case reverses the order:
when the right operand's type is a subclass of the left's and overrides the reflected method,
Python tries that reflected method first,
so the more specific type can answer before its base does.

Both methods declare `-> Meters` even though each can return `NotImplemented`,
and that is the standard convention rather than a shortcut.
Typeshed annotates `timedelta.__add__()` as returning `timedelta`, not a union,
and it can do that because it gives `NotImplemented` a type that inherits from `Any`,
so returning the sentinel satisfies any declared return type.
Writing the union out, `Meters | NotImplementedType`,
makes a checker reject `(Meters(1) + Meters(2)).n`,
since the sentinel branch has no `n`.
The sentinel signals the interpreter and never reaches a caller,
so an annotation that names it describes the wrong thing.
Widening the return to `Any` describes nothing and turns off checking for every caller.

[Composite and Interpreter](34_Composite_and_Interpreter.md#interpreter)
builds the expression system this chapter opened with,
using these two methods to let Python's own parser assemble the tree.

## Turning One Unknown Type Into a Second Dispatch

Three techniques in this chapter do the same thing.
The `eval_*()` family, the `OUTCOME` table,
and `__add__()` with `__radd__()` all take a type the first dispatch could not resolve and dispatch again on it.
They differ in who performs the second dispatch and where the answers live.
The methods make the language do it and scatter the answers across the classes.
The table does it with a dictionary probe and collects the answers in one place.
The operators are the one case where Python performs the second dispatch for you.
Everywhere else you choose between paying for the second dispatch in methods or paying for it in data.

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
3.  In `test_paper_scissors.py`, add `Lizard`'s seven matchups to `EXPECTED`,
    taking it from nine entries to sixteen,
    and confirm both versions still agree with each other and with `EXPECTED`.
4.  In `arena.py`, give `item_pair_gen()` an optional `counts: Counter[str] | None = None` parameter that it updates in place with a tally of every item type it chooses,
    while still yielding `(item1, item2)` pairs so existing calls need no change.
    Pass in your own `Counter` and print how many times `Lizard` appeared after iterating over all 100 pairs from `item_pair_gen(Item, 100, counts)`,
    since the counter fills only as you consume the generator.
5.  Give `Meters` a `__sub__()` and a `__rsub__()`.
    `__sub__()` handles a `Meters`, an `int`, or a `float`,
    and returns `NotImplemented` for anything else.
    `__rsub__()` needs only the `int` and `float` cases,
    since Python never calls the reflected form for two `Meters`.
    Subtraction does not commute, so the reflected form must undo the swap:
    check that `10 - Meters(3)` produces `Meters(7)` rather than `Meters(-7)`.
    Then confirm that `"ten" - Meters(3)` raises `TypeError` rather than building anything.
6.  Subclass `Paper` as `Origami` and duel it against `Rock` in the table version,
    as `exact_match.py` does.
    Explain the `KeyError` in terms of how the lookup matches.
    Then make the table tolerate subclasses by walking `type(item).__mro__` for the first class that has a row,
    and say which of the two properties named after the table listing you have just given up.
7.  Create a business-modeling environment with three types of `Inhabitant`:
    `Dwarf` (for engineers), `Elf` (for marketers) and `Troll` (for managers).
    Now create a class called `Project` that creates the different inhabitants and causes them to `interact()` with each other.
    Single dispatch is enough here; the next exercise adds the second dispatch.
8.  Modify the above example to make the interactions more detailed.
    Each `Inhabitant` can randomly produce a `Weapon` using `get_weapon()`:
    a `Dwarf` uses `Jargon` or `Play`,
    an `Elf` uses `InventFeature` or `SellImaginaryProduct`,
    and a `Troll` uses `Edict` and `Schedule`.
    You must decide which weapons "win" and "lose" in each interaction
    (as in `paper_scissors_rock.py`).
    Add a `battle()` method to `Project` that takes two `Inhabitant`s and matches them against each other.
    Now create a `meeting()` method for `Project` that creates groups of `Dwarf`,
    `Elf` and `Troll` and battles the groups against each other until only members of one group remain.
    These are the "winners."
9.  This chapter replaces the double dispatching of `paper_scissors_rock.py` with the table lookup of `paper_scissors_rock_table.py`.
    When is the table lookup more appropriate than hard-coding the dynamic dispatch?
    Can you keep the syntactic simplicity of the dispatch while using a table underneath?
10. Modify Exercise 8 to use the table lookup technique of `paper_scissors_rock_table.py`.
