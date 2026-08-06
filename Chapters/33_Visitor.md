# Visitor

The *Visitor* pattern uses *Multiple Dispatching*.
People can confuse the two by looking at the implementation rather than the intent.

The *Visitor* assumption is that you have a primary class hierarchy you cannot change.
Perhaps it's from another vendor and you can't touch its source.
However, you'd like to add new polymorphic methods to it.
Normally you'd add something to the base class interface,
but that's not an option.
How do you get around this?

*Visitor*, the final pattern in *GoF Design Patterns*,
solves this kind of problem.
It allows you to extend the interface of the primary class hierarchy.
It requires that the primary class hierarchy have a method,
typically called `accept()`,
which takes an object of a secondary class hierarchy called `Visitor`.
The operations on the primary hierarchy become dynamically bound.
The objects of the primary hierarchy simply `accept()` the `Visitor`,
then call the `Visitor`'s dynamically bound method:

```python
# flower_visitors.py
import random
from collections.abc import Iterator
from typing import Any, override

# The Flower hierarchy cannot be changed:
class Flower:
    def accept(self, visitor: Any) -> None:
        visitor.visit(self)
    def pollinate(self, pollinator: Visitor) -> None:
        print(self, "pollinated by", pollinator)
    def eat(self, eater: Visitor) -> None:
        print(self, "eaten by", eater)
    def __str__(self) -> str:
        return self.__class__.__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass

class Chrysanthemum(Flower):
    @override
    def eat(self, eater: Visitor) -> None:
        print(self, "is toxic to", eater)

# The secondary hierarchy accepted by Flower:
class Visitor:
    def __str__(self) -> str:
        return self.__class__.__name__

class Bug(Visitor):
    pass
class Pollinator(Bug):
    pass
class Predator(Bug):
    pass

# Bee pollinates:
class Bee(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

# Fly also pollinates:
class Fly(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

# Worm eats instead:
class Worm(Predator):
    def visit(self, flower: Flower) -> None:
        flower.eat(self)

def flower_gen(n: int) -> Iterator[Flower]:
    flowers = Flower.__subclasses__()
    for _ in range(n):
        yield random.choice(flowers)()

# Now perform Bug operations on the flowers:
bee = Bee()
fly = Fly()
worm = Worm()
random.seed(47)  # Reproducible flower sequence
for flower in flower_gen(4):
    flower.accept(bee)
    flower.accept(fly)
    flower.accept(worm)
#: Ranunculus pollinated by Bee
#: Ranunculus pollinated by Fly
#: Ranunculus eaten by Worm
#: Gladiolus pollinated by Bee
#: Gladiolus pollinated by Fly
#: Gladiolus eaten by Worm
#: Ranunculus pollinated by Bee
#: Ranunculus pollinated by Fly
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum pollinated by Fly
#: Chrysanthemum is toxic to Worm
```

The `accept()`/`visit()` pair is the *double dispatch*.
`accept()` hands the concrete flower to the visitor,
`visit()` resolves the visitor's type,
and the `pollinate()` or `eat()` call inside `visit()` resolves the flower's type.
In the classic pattern every element class overrides `accept()`,
which is where the element's type is resolved;
here one inherited `accept()` is enough,
because the flower's type is resolved a step later.
The last line of output shows both dispatches doing visible work.
`Chrysanthemum` overrides `eat()`
(chrysanthemums really do produce a natural insecticide),
so that line depends on both unknown types at once:
the worm's type chose `eat()`, and the flower's type chose which `eat()` runs.
If you delete the override, the program still runs;
the flower-side dispatch simply goes back to having nothing to say.

Notice where the behavior lives.
The classic pattern overloads `visit()` once per flower type and keeps each operation's body in the visitor,
so the only addition to the primary hierarchy is `accept()`.
Python has no overloading,
so this version puts the type-specific behavior in `pollinate()` and `eat()` on the flowers instead,
and the visitors choose between them.
Whichever way you write it,
the primary hierarchy ends up carrying code it was supposed to be spared.

One annotation in the listing looks like a shortcut and is not.
`accept()` types its visitor as `Any`,
because the `Visitor` base class declares no `visit()` method,
so declaring that parameter as `Visitor` instead of `Any` fails the type checker.
The classic pattern fixes this by declaring `visit()` abstract on the visitor base.
A `Protocol` removes the `Any` in four lines:

    class Visits(Protocol):
        def visit(self, flower: Flower) -> None: ...

    class Flower:
        def accept(self, visitor: Visits) -> None:
            visitor.visit(self)

The listing keeps `Any` because the empty `Visitor` base is what the classic pattern looks like,
and seeing the price is part of the point.
This `Any` is chosen,
unlike the one in [Data Transfer Objects](22_Data_Transfer_Objects.md),
where a bag of attributes named at runtime leaves no precise type to write.

## The Pythonic Visitor: singledispatch

Python can add a method to a fixed hierarchy from outside,
using `functools.singledispatch`.
It turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
That's how *Visitor* works,
but without the `accept()` hook or the `Visitor` class hierarchy:

```python
# visitor_singledispatch.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

# A new operation, defined outside the Flower hierarchy:
@singledispatch
def nectar(flower: Flower) -> str:
    return f"{flower}: no nectar"

@nectar.register
def _(flower: Gladiolus) -> str:
    return f"{flower}: abundant nectar"

@nectar.register
def _(flower: Chrysanthemum) -> str:
    return f"{flower}: a little nectar"

# A second operation, added independently of the first:
@singledispatch
def fragrance(flower: Flower) -> str:
    return "faint"

@fragrance.register
def _(flower: Ranunculus) -> str:
    return "strong"

if __name__ == "__main__":
    flowers: list[Flower] = [
        Gladiolus(), Ranunculus(), Chrysanthemum()]
    for f in flowers:
        print(nectar(f), "| fragrance:", fragrance(f))
#: Gladiolus: abundant nectar | fragrance: faint
#: Ranunculus: no nectar | fragrance: strong
#: Chrysanthemum: a little nectar | fragrance: faint
```

Each registered implementation above is named `_`.
`nectar()` calls it through the dispatcher, never by its own name,
so the name carries no meaning.
`_` is the conventional placeholder for a name nobody will use.
Reusing `_` for every registration is safe:
`@nectar.register` stores the function in its dispatch table before the next `def _` rebinds the name,
so nothing is lost.

Nothing touches `Flower`.
Each operation is a separate function,
and the `@singledispatch` default handles any type you have not registered.
Dispatch follows inheritance:
an unregistered subclass uses its nearest registered ancestor,
falling back to the `Flower` default only when no ancestor is registered
(the tests below pin this down).

The default is also the risk.
A new `Flower` subclass that nobody registers gets the default answer with no exception and no static complaint,
so a forgotten registration shows up as a wrong result rather than a failure.
When there is no sensible answer for an unregistered type,
give the base function a `raise NotImplementedError(f"no nectar rule for {type(flower).__name__}")` instead of a fallback string,
and the omission fails at the first call.
A `match` over a closed union of types goes further and catches it before the program runs
([Composite and Interpreter](34_Composite_and_Interpreter.md#a-composite-of-data-classes)),
at the price of a set of types no one else can extend.
A union annotation, `flower: Gladiolus | Ranunculus`,
registers one implementation for several types at once.
Adding a new operation is a new function.
Adding a new flower is a class and, where needed, a one-line registration.
When the operation should read like a method,
use `functools.singledispatchmethod` instead.

*Visitor* still has a place:
when you truly cannot define functions over the hierarchy,
or you need the `accept()` hook for some other reason.
But in Python that is rare.
As with [Pattern Refactoring](37_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)'s recycling-note example,
`singledispatch` is the open-method mechanism that *Visitor* fakes.

Because each operation is a plain function, testing is direct.
Call it with each flower type and assert the result.
The cases worth covering are the registered types,
the `@singledispatch` default for an unregistered type,
and that the two operations dispatch independently:

```python
# test_visitor.py
import pytest
from visitor_singledispatch import (
    Chrysanthemum,
    Flower,
    Gladiolus,
    Ranunculus,
    fragrance,
    nectar,
)

def test_nectar_registered_types() -> None:
    assert nectar(Gladiolus()) == "Gladiolus: abundant nectar"
    assert nectar(Chrysanthemum()) == "Chrysanthemum: a little nectar"

def test_nectar_default_for_unregistered() -> None:
    assert nectar(Ranunculus()) == "Ranunculus: no nectar"
    assert nectar(Flower()) == "Flower: no nectar"

@pytest.mark.parametrize("flower, expected", [
    (Ranunculus(), "strong"),
    (Gladiolus(), "faint"),
    (Chrysanthemum(), "faint"),
])
def test_fragrance_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert fragrance(flower) == expected

def test_operations_dispatch_independently() -> None:
    # Nectar knows Gladiolus and Chrysanthemum; fragrance knows
    # Ranunculus. A Ranunculus falls to nectar's default but hits
    # fragrance's registered case.
    ranunculus = Ranunculus()
    assert nectar(ranunculus) == "Ranunculus: no nectar"
    assert fragrance(ranunculus) == "strong"

def test_dispatch_follows_inheritance() -> None:
    # Unregistered subclass: nearest registered ancestor wins
    class Hybrid(Gladiolus):
        pass

    assert nectar(Hybrid()) == "Hybrid: abundant nectar"
```

## One Dispatch Is Enough

*Visitor* dispatches twice, and `singledispatch` dispatches once.
Nothing was lost in the trade.
The second dispatch in the classic pattern is not there because two types are unknown;
it is there because the operation has nowhere else to live.
The visitor's type stands in for the operation,
so the language must resolve it at runtime along with the element's type.
Once an operation can be a function defined outside the hierarchy,
calling `nectar()` instead of `fragrance()` selects the operation before anything runs,
and only the flower's type is still unknown.
One dispatch covers it.

That is the intent difference the chapter opened with.
*Visitor* adds operations to a hierarchy you cannot edit,
and its double dispatch is the means.
*Multiple Dispatching* is the end in itself:
two objects whose types are both unknown until runtime have to interact,
as in `paper_scissors_rock.py`.
`singledispatch` dispatches on the first argument only,
so it does nothing for that second problem.
When two types must genuinely resolve together,
use the table keyed by a tuple of types from [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many).

## Exercises

1.  Create a business-modeling environment with three types of `Inhabitant`:
    `Dwarf` (for engineers), `Elf` (for marketers) and `Troll` (for managers).
    Now create a class called `Project` that creates the different inhabitants and causes them to `interact()` with each other using *Multiple Dispatching*.
2.  Modify the above example to make the interactions more detailed.
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
3.  [Multiple Dispatching](32_Multiple_Dispatching.md)
    replaces the double dispatching of `paper_scissors_rock.py` with the table lookup of `paper_scissors_rock_table.py`.
    When is the table lookup more appropriate than hard-coding the dynamic dispatch?
    Can you keep the syntactic simplicity of the dispatch while using a table underneath?
4.  Modify Exercise 2 to use the table lookup technique of `paper_scissors_rock_table.py`.
5.  Rewrite `flower_visitors.py` with `singledispatch`:
    make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
    with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
    Which classes and which methods disappear?
6.  Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
    then add a third operation, `thorns()`, over all four flowers.
    Count the lines each change costs,
    and say which of the two `@singledispatch` makes cheaper.
