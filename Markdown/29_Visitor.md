# Visitor

The *Visitor* pattern uses *Multiple Dispatching*.
People can confuse the two by looking at the implementation rather than the intent.

The assumption is that you have a primary class hierarchy that is unchangeable.
Perhaps it's from another vendor and you can't make changes to that hierarchy.
However, you'd like to add new polymorphic methods to that hierarchy.
Normally you'd have to add something to the base class interface, but that's unchangeable.
How do you get around this?

*Visitor*, the final pattern in the *Design Patterns* book, solves this kind of problem.
It allows you to extend the interface of the primary type.
It does this by creating a separate class hierarchy of type `Visitor` to virtualize the operations performed upon the primary type.
The objects of the primary type simply "accept" the visitor,
then call the visitor's dynamically-bound method:

```python
# flower_visitors.py
# Demonstration of "visitor" pattern.
import random
from collections.abc import Iterator
from typing import Any

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
class Runuculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

# The companion class accepted by Flower:
class Visitor:
    def __str__(self) -> str:
        return self.__class__.__name__

class Bug(Visitor):
    pass
class Pollinator(Bug):
    pass
class Predator(Bug):
    pass

# Add the ability to do "Bee" activities:
class Bee(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

# Add the ability to do "Fly" activities:
class Fly(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

# Add the ability to do "Worm" activities:
class Worm(Predator):
    def visit(self, flower: Flower) -> None:
        flower.eat(self)

def flower_gen(n: int) -> Iterator[Flower]:
    flwrs = Flower.__subclasses__()
    for i in range(n):
        yield random.choice(flwrs)()

# It's almost as if I had a method to Perform
# various "Bug" operations on all Flowers:
bee = Bee()
fly = Fly()
worm = Worm()
for flower in flower_gen(10):
    flower.accept(bee)
    flower.accept(fly)
    flower.accept(worm)
```

The `accept()`/`visit()` pair is *double dispatch*:
`accept()` resolves the flower's type,
then `visit()` resolves the visitor's type.

## The Pythonic Visitor: singledispatch

Python can add a method to a fixed hierarchy from outside,
with `functools.singledispatch`.
It turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
That is exactly how *Visitor*'s works,
but without the `accept()` hook or the `Visitor` class hierarchy:

```python
# visit_singledispatch.py
# Adding operations to a fixed hierarchy without touching it, the
# Python way.
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Runuculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

# A new operation, defined entirely outside the Flower hierarchy:
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
def _(flower: Runuculus) -> str:
    return "strong"

if __name__ == "__main__":
    flowers: list[Flower] = [
        Gladiolus(), Runuculus(), Chrysanthemum()]
    for f in flowers:
        print(nectar(f), "| fragrance:", fragrance(f))
```

`Flower` is never touched.
Each operation is a separate function,
and the `@singledispatch` default handles any type you have not registered.
Adding a new operation is a new function; adding a new flower is a class plus,
where needed, a one-line registration.
When the operation should read like a method,
use `functools.singledispatchmethod` instead.

*Visitor* still has a place:
when you truly cannot define functions over the hierarchy,
or you need the `accept()` hook for some other reason.
But in Python that is rare.
As with [the Pattern Refactoring chapter](30_Pattern_Refactoring.md)'s price-and-weight example,
`singledispatch` is the open-method mechanism that *Visitor* fakes.

## Verifying the Operations

Because each operation is a plain function, testing is direct:
call it with each flower type and assert the result.
The cases worth covering are the registered types,
the `@singledispatch` default for an unregistered type,
and the fact that the two operations dispatch independently:

```python
# test_visitor.py
from visit_singledispatch import (
    Chrysanthemum,
    Flower,
    Gladiolus,
    Runuculus,
    fragrance,
    nectar,
)

def test_nectar_registered_types() -> None:
    assert nectar(Gladiolus()) == "Gladiolus: abundant nectar"
    assert nectar(Chrysanthemum()) == "Chrysanthemum: a little nectar"

def test_nectar_default_for_unregistered() -> None:
    assert nectar(Runuculus()) == "Runuculus: no nectar"
    assert nectar(Flower()) == "Flower: no nectar"

def test_fragrance_registered_and_default() -> None:
    assert fragrance(Runuculus()) == "strong"
    assert fragrance(Gladiolus()) == "faint"
    assert fragrance(Chrysanthemum()) == "faint"

def test_operations_dispatch_independently() -> None:
    # Nectar knows Gladiolus and Chrysanthemum; fragrance knows
    # Runuculus. A Runuculus falls to nectar's default but hits
    # fragrance's registered case.
    runuculus = Runuculus()
    assert nectar(runuculus) == "Runuculus: no nectar"
    assert fragrance(runuculus) == "strong"
```

## Exercises

1.  Create a business-modeling environment with three types of `Inhabitant`:
    `Dwarf` (for engineers), `Elf` (for marketers) and `Troll` (for managers).
    Now create a class called `Project` that creates the different inhabitants and causes them to `interact()` with each other using *Multiple Dispatching*.
2.  Modify the above example to make the interactions more detailed.
    Each `Inhabitant` can randomly produce a `Weapon` using `get_weapon()`:
    a `Dwarf` uses `Jargon` or `Play`,
    an `Elf` uses `InventFeature` or `SellImaginaryProduct`,
    and a `Troll` uses `Edict` and `Schedule`.
    You must decide which weapons "win" and "lose" in each interaction (as in `paper_scissors_rock.py`).
    Add a `battle()` method to `Project` that takes two `Inhabitant`s and matches them against each other.
    Now create a `meeting()` method for `Project` that creates groups of `Dwarf`,
    `Elf` and `Troll` and battles the groups against each other until only members of one group remain.
    These are the "winners."
3.  Modify `paper_scissors_rock.py` to replace the double dispatching with a table lookup.
    The simplest way is a `dict` keyed by a tuple of the two objects' types,
    looked up as `table[type(o1), type(o2)]` (this is what `paper_scissors_rock2.py` does).
    When is the table lookup more appropriate than hard-coding the dynamic dispatch?
    Can you keep the syntactic simplicity of the dispatch while using a table underneath?
4.  Modify Exercise 2 to use the table lookup technique described in Exercise 3.
