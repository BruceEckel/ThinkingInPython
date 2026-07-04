# Visitor

The *Visitor* pattern uses *Multiple Dispatching*.
People can confuse the two by looking at the implementation rather than the intent.

The *Visitor* assumption is that you have a primary class hierarchy that is unchangeable.
Perhaps it's from another vendor and you can't make changes to that hierarchy.
However, you'd like to add new polymorphic methods to that hierarchy.
Normally you'd have to add something to the base class interface, but that's unchangeable.
How do you get around this?

*Visitor*, the final pattern in *GoF Design Patterns*, solves this kind of problem.
It allows you to extend the interface of the primary class hierarchy.
It requires that the primary class hierarchy have a method,
typically called `accept()`, which takes an object of a secondary class hierarchy called `Visitor`.
This virtualizes the operations performed upon the primary hierarchy.
The objects of the primary hierarchy simply `accept()` the `Visitor`,
then call the `Visitor`'s dynamically bound method:

```python
# flower_visitors.py
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
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

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

# Now we can perform Bug operations on Flowers:
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
#: Chrysanthemum eaten by Worm
```

The `accept()`/`visit()` pair is the *double dispatch*:
`accept()` resolves the flower's type,
then `visit()` resolves the visitor's type.

## The Pythonic Visitor: singledispatch

Python can add a method to a fixed hierarchy from outside, using `functools.singledispatch`.
This turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
That is exactly how *Visitor* works,
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

`Flower` is never touched.
Each operation is a separate function,
and the `@singledispatch` default handles any type you have not registered.
Adding a new operation is a new function; adding a new flower is a class and,
where needed, a one-line registration.
When the operation should read like a method,
use `functools.singledispatchmethod` instead.

*Visitor* still has a place:
when you truly cannot define functions over the hierarchy,
or you need the `accept()` hook for some other reason.
But in Python that is rare.
As with [Pattern Refactoring](35_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)'s price-and-weight example,
`singledispatch` is the open-method mechanism that *Visitor* fakes.

Because each operation is a plain function, testing is direct:
call it with each flower type and assert the result.
The cases worth covering are the registered types,
the `@singledispatch` default for an unregistered type,
and that the two operations dispatch independently:

```python
# test_visitor.py
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

def test_fragrance_registered_and_default() -> None:
    assert fragrance(Ranunculus()) == "strong"
    assert fragrance(Gladiolus()) == "faint"
    assert fragrance(Chrysanthemum()) == "faint"

def test_operations_dispatch_independently() -> None:
    # Nectar knows Gladiolus and Chrysanthemum; fragrance knows
    # Ranunculus. A Ranunculus falls to nectar's default but hits
    # fragrance's registered case.
    runuculus = Ranunculus()
    assert nectar(runuculus) == "Ranunculus: no nectar"
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
3.  [Multiple Dispatching](32_Multiple_Dispatching.md) replaces the double dispatching of `paper_scissors_rock.py` with the table lookup of `paper_scissors_rock_table.py`.
    When is the table lookup more appropriate than hard-coding the dynamic dispatch?
    Can you keep the syntactic simplicity of the dispatch while using a table underneath?
4.  Modify Exercise 2 to use the table lookup technique of `paper_scissors_rock_table.py`.
