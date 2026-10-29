# Multiple Dispatching

> Two objects meet, and the right action depends on the type of each.
> *Multiple Dispatching* chooses the action from both types at once.

Code that combines several interacting types can end up with a type test for every combination.
Consider a system that parses and executes mathematical expressions.
You want to say `Number + Number`, `Number * Number`, etc.,
where `Number` is the base class for a family of numerical objects.
But when you say `a + b`,
and you don't know the exact type of either `a` or `b`,
how does the code choose the operation that fits both types?

Python dispatches on one type at a time.
When two objects of unknown type interact,
a method call resolves its receiver's type alone.
You end up testing the other type in your own code,
writing out the dispatch the language performs for the receiver.

That dispatch is one form of [polymorphism](20_Patterns--Rethinking_Objects.md#what-is-polymorphism),
which broadly means that a function accepts arguments of more than one type.
Polymorphism takes three forms.
Function overloading in C++ picks a function from the argument types.
Generics write one body that works across many types.
This chapter uses the third form,
the runtime dispatch that inheritance provides.
Runtime dispatch resolves on the type of one object,
the one receiving the method call.

The solution is *Multiple Dispatching*.
To dispatch on two unknown types through methods, you need two method calls.
The first resolves the first type, and the second resolves the second.
Two unknown types means two dispatches, which is *double dispatching*.
In `paper_scissors_rock.py`,
both interacting objects come from a single hierarchy.
The two dispatches go through methods named `compete()` and `eval_*()`.
If two different type hierarchies interact,
you need a dispatching method call for each hierarchy.

When the interaction is an operator,
Python performs this second dispatch for you.
If `a.__add__(b)` declines, `a + b` retries as `b.__radd__(a)`.
That [retry](#operators-dispatch-twice)
answers the opening `Number + Number` question.
Before that section,
this chapter builds the general technique for any other interaction,
where you write the second dispatch yourself.
The working example is a game of paper, scissors, rock.

The chapter builds the game twice,
once dispatching through methods and once looking up a table.
Both versions share one result type, `Outcome`,
an enumeration whose members are `WIN`, `LOSE`, and `DRAW`.
`Outcome` is a [`StrEnum`](12_Techniques--Data_Classes_as_Types.md#enum-mix-ins),
so each member is its string value and prints as `win`, `lose`, or `draw`:

```python
# outcome.py
from enum import StrEnum

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
```

You also need two small helper functions, one to generate every pair of items,
and one to play a pair off and print the result:

```python
# arena.py
from collections.abc import Iterator
from itertools import product
from typing import Any

def all_pairs[T](base: type[T]) -> Iterator[tuple[T, T]]:
    kinds = base.__subclasses__()
    for a, b in product(kinds, kinds):
        yield a(), b()

def duel(player: Any, opponent: Any) -> None:
    result = player.compete(opponent)
    print(f"{player} <--> {opponent} : {result}")
```

`__subclasses__()` lists the base's direct subclasses,
as [`shape_name()`](26_Patterns--Factory.md#simple-factory-method) does.
`itertools.product()` pairs each subclass with every subclass, itself included,
so a demo prints each of the nine answers once.
`duel()` annotates both parameters `Any` because `paper_scissors_rock.py` and `paper_scissors_rock_table.py` define separate `Item` hierarchies,
and this file must serve both.

## Two Dispatches Through Methods

```python
# paper_scissors_rock.py
from typing import Any
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def compete(self, opponent: Any) -> Outcome:
        # First dispatch: self was Paper
        return opponent.eval_paper(self)
    def eval_paper(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Paper, and it draws
        return Outcome.DRAW
    def eval_scissors(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Scissors, and it wins
        return Outcome.WIN
    def eval_rock(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Rock, and it loses
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, opponent: Any) -> Outcome:
        # First dispatch: self was Scissors
        return opponent.eval_scissors(self)
    def eval_paper(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Paper, and it loses
        return Outcome.LOSE
    def eval_scissors(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Scissors, and it draws
        return Outcome.DRAW
    def eval_rock(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Rock, and it wins
        return Outcome.WIN

class Rock(Item):
    def compete(self, opponent: Any) -> Outcome:
        # First dispatch: self was Rock
        return opponent.eval_rock(self)
    def eval_paper(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Paper, and it wins
        return Outcome.WIN
    def eval_scissors(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Scissors, and it loses
        return Outcome.LOSE
    def eval_rock(self, caller: Any) -> Outcome:
        # Second dispatch: caller was Rock, and it draws
        return Outcome.DRAW
```

A loop over `all_pairs(Item)` plays each of the nine pairs through `duel()`:

```python
# methods_demo.py
from arena import all_pairs, duel
from paper_scissors_rock import Item

for player, opponent in all_pairs(Item):
    duel(player, opponent)
#: Paper <--> Paper : draw
#: Paper <--> Scissors : lose
#: Paper <--> Rock : win
#: Scissors <--> Paper : win
#: Scissors <--> Scissors : draw
#: Scissors <--> Rock : lose
#: Rock <--> Paper : lose
#: Rock <--> Scissors : win
#: Rock <--> Rock : draw
```

![](_images/double_dispatch)

Follow one duel to see which item each result describes.
`scissors.compete(paper)` resolves `self` to `Scissors`, the first dispatch,
and calls `paper.eval_scissors(...)`.
That call is the second dispatch.
It resolves `paper` and runs `Paper.eval_scissors()`,
the one method that the two dispatches together select.
Its class is `Paper`.
Its name says `Scissors`.
Which item does that method's result describe?
`Paper.eval_scissors()` returns `WIN`.
Scissors cut paper, so that is the outcome for the scissors that started the duel,
not for the `Paper` whose code is running.
`methods_demo.py` reports it that way: `Scissors <--> Paper : win`.
Every `eval_*()` method returns the outcome for the original caller,
the type named in the method's own name.
If you read that convention the other way,
every `eval_*()` result appears reversed.

The `caller` argument of each `eval_*()` method is the same object `compete()` held as `self` before passing it along.
A game whose outcome depends on the caller's state reads that state through `caller`.
This game ignores the argument,
since the outcome depends on the two types alone.

`Item` declares `__str__()` alone,
so each `opponent` and `caller` parameter takes `Any`.
Those `Any` annotations turn off static checking.
Classes that supply eight of the nine answers then pass the type checker.
Python raises an `AttributeError` at the first duel that calls the ninth.
A precise type needs a declaration of all four methods,
either on `Item` as abstract methods or in a `Protocol`.
Declaring the four methods restores the checking,
but the declaration repeats every class's method names.

## One Lookup in a Table

In `paper_scissors_rock.py`,
each `Item` type encodes the answers for its own combinations.
Together the answers form a table spread across the classes.
That table is hard to maintain.
Changing who wins one pairing means editing two methods in two classes,
and a new `Item` class needs a new method in every existing class.
Writing the table out as data puts all nine answers in one place:

```python
# paper_scissors_rock_table.py
from typing import Final
from outcome import Outcome

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)]
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
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
```

The table version keeps the checking and drops the repetition.
Its `Item` declares the one method the dispatch needs,
so `compete()` takes its opponent as an `Item`.
Its answers are rows in one dictionary,
so a new class inherits `compete()` and needs rows instead of methods.
The type checker accepts a table that lacks a row, though,
the way it accepts a class that lacks a method.
A table that holds eight of the nine answers fails at the first duel that needs the ninth.

A tuple works as a dictionary key, the same as a single object,
so each key in `OUTCOME` is a pair of classes.
The same `all_pairs()` loop over these classes prints the same nine duels that `methods_demo.py` prints.

Both versions now hold the same nine answers, one for each pair of types:

![](_images/dispatch_story)

With the nine answers drawn as a grid,
the versions differ in where each one keeps the grid.
The method version stores one column of the grid in each class,
so finding a cell takes two dispatches.
The table version stores the whole grid in `OUTCOME`,
so one lookup finds the same cell.

The dashed fourth item shows what adding a class requires of each version.
In the method version,
a new class requires a new `eval_*()` method in every existing class,
while the table version adds rows to `OUTCOME` and leaves the classes as they are.

The lookup shares two properties with the [table-driven state machine](31_Patterns--State_Machines.md#the-engine).
It matches classes exactly, so a subclass of `Paper` needs rows of its own.
And a missing pair fails at the first duel that needs it,
the fail-fast policy that suits a table you are still filling in
(see exercise 1).
Here the failure is the dictionary's own `KeyError`,
where the state machine's engine raises `NoTransition`.

The lookup raises a `KeyError` for a subclass:

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
so `(Origami, Rock)` and `(Paper, Rock)` are different keys,
however closely the two classes relate.
The lookup ignores the [MRO](07_Foundations--Classes.md#method-resolution-order).

## One Type or Many

For dispatch on one argument's type, `functools.singledispatch` gives you open,
per-type functions, as [*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
shows.
For dispatch on two or more types at once,
the `OUTCOME` table is the idiomatic answer: a `dict` keyed by a tuple of types.
Adding a new `Item` then means adding rows to the table and leaving the classes as they are.

`singledispatch` and the table match types differently.
`singledispatch` resolves through the MRO,
so a function registered for a base class serves every subclass.
The table matches the class exactly.
Swapping one for the other changes whether a subclass gets its base class's answer,
as well as how many types the dispatch reads.

### `match` with Class Patterns

A `match` statement with class patterns is a third option for a two-type decision.
Like `singledispatch`, it matches subclasses.
A class pattern tests with `isinstance()`,
so a subclass matches the pattern its base does:

```python
# match_dispatch.py
from outcome import Outcome
from paper_scissors_rock_table import Item, Paper, Rock

class Origami(Paper):
    pass

def compete(player: Item, opponent: Item) -> Outcome:
    match player, opponent:
        case Paper(), Rock():
            return Outcome.WIN
        case Rock(), Paper():
            return Outcome.LOSE
        case _:
            raise ValueError(f"{player}, {opponent}")

print(compete(Origami(), Rock()))
#: win
```

`Origami()` matches the `Paper()` pattern,
though the table lookup in `exact_match.py` raises a `KeyError` for the same subclass.

`singledispatch` is open.
Any module can register a function for a new type.
A `match` keeps every case together in one block, closed the way the table is,
so adding an `Item` means adding cases to that block.

`match` tries its cases from the top and takes the first that matches,
where `singledispatch` picks the most specific registered class.
A case for `Origami` must therefore come before the `Paper()` case.
Placed after it, the `Origami` case is dead code,
because the `Paper()` pattern matches the subclass first.

### The `singledispatchmethod` Trap

[`functools.singledispatchmethod`](41_Functional--Toolkits.md#singledispatchmethod)
supplies the second dispatch for a method.
Ordinary method resolution dispatches on `self` and finds the decorated method,
which then dispatches on the first argument after `self` through `singledispatch`.
That is the pair of dispatches the `eval_*()` family writes out.
`singledispatchmethod` matches on the MRO, like `singledispatch`,
rather than exactly.

Declaring the `@singledispatchmethod` on a shared base is a mistake that runs and gives wrong answers.
The base then holds one dispatcher that every subclass inherits.
Because resolving `self` finds that same dispatcher for every subclass,
each class needs its own `@singledispatchmethod`.
The listing below makes the mistake,
so `Paper().compete(Rock())` prints the answer registered through `Rock.compete`:

```python
# singledispatch_trap.py
from functools import singledispatchmethod

class Item:
    @singledispatchmethod
    def compete(self, opponent: object) -> str:
        raise NotImplementedError

class Paper(Item):
    pass

class Rock(Item):
    pass

@Paper.compete.register  # type: ignore  # [1]
def _(self: Item, opponent: Rock) -> str:
    return "paper wins"

@Rock.compete.register  # type: ignore  # [2]
def _(self: Item, opponent: Rock) -> str:
    return "rock draws"

print(Paper().compete(Rock()))
#: rock draws
print(Rock().compete(Rock()))
#: rock draws
```

`Paper` and `Rock` both inherit `Item.compete`,
so both registrations attach to that one dispatcher.
The `@register` at `[2]` silently overwrites the entry `[1]` made for `Rock`.
The `singledispatch` lookup ignores `self`'s type,
so both duels return the same answer,
although each registration went through its own class.

## Methods or Table

Most programmers first write a third version:
an `isinstance()` ladder inside `compete()`,
testing the opponent's type case by case.
It works.
The type tests repeat in every class,
as the `eval_*()` methods do in the method version.
The programmer writes the type tests that dispatch performs on its own.
Every new `Item` requires an edit to every ladder.
Both versions in this chapter replace the ladder.

The method version puts `eval_paper()`, `eval_scissors()`,
and `eval_rock()` on every class.
It comes from languages where a table keyed by a pair of types is awkward to write.
There, spreading the table across the classes is the easier form.
A Python `dict` takes a tuple of classes as a key,
so the table version is shorter,
and adding a class means adding rows to one dictionary.
A table cell can hold a function, so even elaborate behavior fits the table
(see exercise 9).

Use the method version when the behavior for a combination belongs to the class rather than to the pairing:
when it reads the object's own state,
or when a subclass should be able to override one combination and inherit the rest.
A combination has two sides, one for each order of the duel,
so the subclass overrides `compete()` for its own side and one `eval_*()` method for the other:

```python
# paper_scissors_rock_subclass.py
from typing import Any
from arena import duel
from outcome import Outcome
from paper_scissors_rock import Paper, Rock, Scissors

class DampPaper(Paper):
    def compete(self, opponent: Any) -> Outcome:
        if isinstance(opponent, Rock):
            return Outcome.DRAW  # Too soggy to wrap
        return super().compete(opponent)
    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.DRAW  # Rock's side of the same draw

duel(DampPaper(), Rock())
#: DampPaper <--> Rock : draw
duel(Rock(), DampPaper())
#: Rock <--> DampPaper : draw
duel(DampPaper(), Scissors())
#: DampPaper <--> Scissors : lose
```

`DampPaper`'s own result against `Rock` comes from `Rock.eval_paper()`,
a method `DampPaper` cannot change,
so its `compete()` returns `DRAW` before making that call.
Because `Rock` has no `eval_damp_paper()` method to receive the dispatch,
that answer takes one `isinstance()` test,
one rung of the ladder that double dispatch replaces.
Both overrides are necessary.
With the `compete()` override alone,
the inherited `Paper.eval_rock()` reports that the rock loses,
so the two orders of one duel disagree.
Every other combination comes from `Paper`,
through `super().compete(opponent)` and the inherited `eval_*()` methods.

The table version has no comparable override.
The lookup matches classes exactly, so `Paper`'s rows apply to `Paper` alone.
`DampPaper` needs seven rows of its own, five of them copies of `Paper`'s rows.
Editing `Paper`'s rows changes the game for every `Paper`.

## Testing Both Versions

Each win/lose/draw result depends on the two types alone,
so a test creates two items, calls `compete()`, and compares the `Outcome`.
The spread-out method version and the table version must return the same `Outcome` for each of the nine combinations.
If they diverge, one of them has a bug.

```python
# test_paper_scissors.py
from types import ModuleType
from typing import Final
import paper_scissors_rock as methods
import paper_scissors_rock_table as table
import pytest
from outcome import Outcome

type Name = str

# (player, opponent): the player's result
EXPECTED: Final[dict[tuple[Name, Name], Outcome]] = {
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

def compete(module: ModuleType, player: Name,
            opponent: Name) -> Outcome:
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, Outcome)
    return result

@pytest.mark.parametrize("module", [table, methods])
@pytest.mark.parametrize("player, opponent", EXPECTED)
def test_versions_match_expected(module: ModuleType,
                                 player: Name,
                                 opponent: Name) -> None:
    expected = EXPECTED[player, opponent]
    assert compete(module, player, opponent) == expected
```

`test_paper_scissors.py` imports the two modules, not their classes.
`getattr(module, player)` looks the class up on whichever module `pytest` passed to `test_versions_match_expected()`,
so one dictionary of nine expected answers, `EXPECTED`,
drives two independent sets of `Paper`, `Scissors`, and `Rock` classes.
Iterating over `EXPECTED` yields its keys,
so `pytest` parametrizes the test with the nine `(player, opponent)` pairs.

`compete()` also checks the result's type.
A `StrEnum` member equals its string,
so a version that returns the bare string `"win"` passes the `==` alone.

## Operators Dispatch Twice

Python's own operators dispatch twice,
which answers the `Number + Number` question that opens this chapter.
`a + b` first tries `type(a).__add__(a, b)`.
If that returns the special value `NotImplemented`,
Python then tries `type(b).__radd__(b, a)`, the *reflected* form of `__add__()`.
`NotImplemented` is a sentinel value,
not the lookalike `NotImplementedError` exception.
Returning `NotImplemented` tells the interpreter to try the other operand's reflected method next.
The first call dispatches on `a`'s type, the reflected call on `b`'s type.
That is double dispatching, built into the language.
The reflected call is how a type written decades after `int` can sit to the right of an `int` in a sum.

Every binary arithmetic and bitwise operator has a reflected form,
named by inserting an `r` before the operator's name: `__rsub__()`,
`__rmul__()`, `__rtruediv__()`.
`@` dispatches the same way, through `__matmul__()` and `__rmatmul__()`.
Python 3.5 added the operator for array libraries such as NumPy.
No built-in type implements either method, so `2 @ 3` raises a `TypeError`.
The in-place forms, `__iadd__()` and its siblings, are a separate family.
They serve `+=`, not `a + b`.
`Meters.__add__()` and `Meters.__radd__()` each print a line when they run,
so the output traces each dispatch:

```python
# radd_dispatch.py
from exceptions import expected
from record import record

@record
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
# int.__add__() declines; Meters.__radd__() handles it
print(4 + Meters(3))
#: __radd__(Meters(n=3), 4)
#: Meters(n=7)
with expected(TypeError):
    Meters(3) + "four"  # Left declines; no str.__radd__()
#: __add__(Meters(n=3), 'four')
#: [TypeError] unsupported operand type(s) for +: 'Meters'
#: and 'str'
```

`4 + Meters(3)` calls `int.__add__()` first,
which returns `NotImplemented` for a `Meters` operand.
The sentinel is a decline rather than an error,
so Python tries `Meters.__radd__()` next.
Its trace line shows the operands in swapped order.
The last case shows why the sentinel exists.
With the left operand declining and no reflected method to try,
Python raises `TypeError`.

Raising a `TypeError` inside `__add__()` ends the expression there,
since the exception propagates immediately.
From inside `__add__()`,
only a returned sentinel makes Python try the right operand's `__radd__()`.

When both operands have the same type, Python tries `__add__()` alone,
so `__add__()` resolves `Meters + Meters`.
Adding two instances of a class that implements `__radd__()` alone raises a `TypeError`.
One case reverses the order.
When the right operand's type is a subclass of the left operand's type and overrides the reflected method,
Python tries that reflected method first,
so the subclass's method runs before the base class's method.

Both methods declare `-> Meters` although each can return `NotImplemented`.
That is the standard convention rather than a shortcut.
Typeshed annotates `timedelta.__add__()` as returning `timedelta`, not a union.
Typeshed can do that because it gives `NotImplemented` a type that inherits from `Any`.
Returning the sentinel then satisfies any declared return type.

Writing the union out, `Meters | NotImplementedType`,
makes `ty` reject `(Meters(1) + Meters(2)).n`,
since the sentinel branch has no `n`.
Pyright and mypy accept the access,
because that inheritance from `Any` makes any attribute access on the sentinel branch type-check.
The sentinel is a signal to the interpreter.
A direct call such as `Meters(3).__add__("four")` does return it.
But the type checker also uses the annotation as the type of the `+` expression that calls `__add__()`,
and no `+` expression evaluates to the sentinel.
An annotation that names it fits the rare direct call and misdescribes every sum.
Widening the return to `Any` tells the type checker that a sum can be any type and turns off checking for every caller.

[*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md#interpreter)
builds the expression system that opens this chapter,
using `__add__()` and `__radd__()` to let Python's own parser assemble the tree.

## Turning One Unknown Type Into a Second Dispatch

Three of this chapter's techniques answer the same question:
what do you do with a type the first dispatch could not resolve?
The `eval_*()` family and `__add__()` with `__radd__()` answer it with a second dispatch,
a second method call that resolves the type by running a method lookup.
The `OUTCOME` table answers it differently.
`Item` defines `compete()` once, and every subclass inherits it.
The body of `compete()`, `OUTCOME[type(self), type(opponent)]`,
is one dictionary lookup keyed on both types at once,
not a second method resolution.

The operators are the one case where the interpreter performs the second dispatch.
Everywhere else you choose between writing a second dispatch in methods and replacing both dispatches with one lookup in data or one `match` statement.

## Exercises

Try each exercise before opening its [solution](../Solutions/32_Patterns--Multiple_Dispatching/).

1.  Add a fourth `Item`, `Lizard`, to `paper_scissors_rock_table.py`.
    Lizard beats Paper and Scissors, and loses to Rock.
    Lizard versus Lizard is a draw.
    Add the seven new entries that `OUTCOME` needs:
    both orders of each mixed pair, plus Lizard versus Lizard.
2.  Add the same `Lizard` to `paper_scissors_rock.py`, the method version,
    which means adding an `eval_lizard()` method to every existing class,
    plus a `Lizard` class with its own `compete()` and four `eval_*()` methods.
    Compare how much code this took versus adding `Lizard` to the table version.
3.  In `test_paper_scissors.py`, add `Lizard`'s seven matchups to `EXPECTED`,
    taking it from nine entries to sixteen,
    and confirm both versions still agree with each other and with `EXPECTED`.
4.  `all_pairs()` yields each pair of types once.
    A tournament of random duels needs a second generator.
    In `arena.py`, write `random_pairs(base, n, counts)`,
    which draws `n` random pairs from `base.__subclasses__()` and yields each as a `(player, opponent)` tuple.
    Give it an optional `counts: Counter[str] | None = None` parameter,
    and have it update that counter in place with a tally of every item type it chooses.
    The counter fills only as you consume the generator,
    so pass in your own `Counter`,
    iterate over all 100 pairs from `random_pairs(Item, 100, counts)`,
    and then print how many times `Lizard` appeared.
5.  Give `Meters` a `__sub__()` and a `__rsub__()`.
    `__sub__()` handles a `Meters`, an `int`, or a `float`,
    and returns `NotImplemented` for anything else.
    `__rsub__()` needs only the `int` and `float` cases,
    since Python skips the reflected form when both operands are `Meters`.
    Subtraction does not commute, so the reflected form must undo the swap.
    Check that `10 - Meters(3)` produces `Meters(7)` rather than `Meters(-7)`.
    Then confirm that `"ten" - Meters(3)` raises a `TypeError` rather than producing a `Meters`.
6.  Subclass `Paper` as `Origami` and duel it against `Rock` in the table version,
    as `exact_match.py` does.
    Explain the `KeyError` in terms of how the lookup matches.
    Then make the table match subclasses by walking both operands' `__mro__` for the first pair that has a row.
    Say what becomes of each of the two properties the lookup shares with the table-driven state machine:
    exact matching, and failure at the first duel that needs a missing pair.
7.  Create a business-modeling environment with three types of `Inhabitant`:
    `Dwarf` (for engineers), `Elf` (for marketers), and `Troll` (for managers).
    Now create a class called `Project` that creates the different inhabitants and causes them to `interact()` with each other.
    Single dispatch is enough here.
    The next exercise adds the second dispatch.
8.  Modify the previous exercise's `Project` to make the interactions more detailed.
    Each `Inhabitant` can randomly produce a `Weapon` using `get_weapon()`:
    a `Dwarf` uses `Jargon` or `Play`,
    an `Elf` uses `InventFeature` or `SellImaginaryProduct`,
    and a `Troll` uses `Edict` or `Schedule`.
    You must decide which weapons "win" and "lose" in each interaction
    (as in `paper_scissors_rock.py`).
    Add a `battle()` method to `Project` that takes two `Inhabitant`s and matches them against each other.
    Now create a `meeting()` method for `Project` that creates groups of `Dwarf`,
    `Elf`, and `Troll` and battles the groups against each other until only members of one group remain.
    These are the "winners."
9.  The chapter claims that a table cell can hold a function,
    so even elaborate behavior fits the table.
    Build that version.
    In `paper_scissors_rock_table.py`,
    give every `OUTCOME` cell a `Callable[[Item, Item], Outcome]` in place of its `Outcome`,
    and have `compete()` call the cell it finds:
    `OUTCOME[type(self), type(opponent)](self, opponent)`.
    The call site stays `player.compete(opponent)`.
    Write a helper that wraps a constant `Outcome` in a callable,
    so the seven unchanged cells stay one line each.
    Then give `Paper` a `wet` attribute and make the `(Paper, Rock)` and `(Rock, Paper)` cells read it.
    Dry paper wraps the rock and wins, wet paper is too soggy and draws,
    whichever of the two calls `compete()`.
    The chapter gives two reasons for preferring the method version.
    Say which one this change answers, and which one survives it.
10. Modify exercise 8 to use the table lookup technique of `paper_scissors_rock_table.py`.
