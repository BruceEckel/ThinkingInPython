# Visitor

The visitor pattern is implemented using multiple dispatching, but
people often confuse the two, because they look at the implementation
rather than the intent.

The assumption is that you have a primary class hierarchy that is fixed;
perhaps it's from another vendor and you can't make changes to that
hierarchy. However, your intent is that you'd like to add new
polymorphic methods to that hierarchy, which means that normally you'd
have to add something to the base class interface. So the dilemma is
that you need to add methods to the base class, but you can't touch the
base class. How do you get around this?

The design pattern that solves this kind of problem is called a
"visitor" (the final one in the *Design Patterns* book), and it builds
on the double dispatching scheme shown in the last section.

The visitor pattern allows you to extend the interface of the primary
type by creating a separate class hierarchy of type `Visitor` to
virtualize the operations performed upon the primary type. The objects
of the primary type simply "accept" the visitor, then call the visitor's
dynamically-bound method:

```python
# flower_visitors.py
# Demonstration of "visitor" pattern.
import random


# The Flower hierarchy cannot be changed:
class Flower:
    def accept(self, visitor):
        visitor.visit(self)
    def pollinate(self, pollinator):
        print(self, "pollinated by", pollinator)
    def eat(self, eater):
        print(self, "eaten by", eater)
    def __str__(self):
        return self.__class__.__name__

class Gladiolus(Flower):
    pass
class Runuculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

class Visitor:
    def __str__(self):
        return self.__class__.__name__

class Bug(Visitor):
    pass
class Pollinator(Bug):
    pass
class Predator(Bug):
    pass

# Add the ability to do "Bee" activities:
class Bee(Pollinator):
    def visit(self, flower):
        flower.pollinate(self)

# Add the ability to do "Fly" activities:
class Fly(Pollinator):
    def visit(self, flower):
        flower.pollinate(self)

# Add the ability to do "Worm" activities:
class Worm(Predator):
    def visit(self, flower):
        flower.eat(self)

def flower_gen(n):
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

The `accept()`/`visit()` pair is *double dispatch*: `accept()` resolves the
flower's type, then `visit()` resolves the visitor's type. The whole apparatus
exists because Java and C++ dispatch on only one type at a time and cannot add a
method to a class from outside it.

## The Pythonic Visitor: singledispatch

Python can add a method to a fixed hierarchy from outside, with
`functools.singledispatch`. It turns a plain function into one that dispatches
on the type of its first argument, with per-type implementations registered from
anywhere. That is precisely Visitor's goal, without the `accept()` hook or the
`Visitor` class hierarchy:

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

`Flower` is never touched. Each operation is a separate function, and the
`@singledispatch` default handles any type you have not registered. Adding a new
operation is a new function; adding a new flower is a class plus, where needed, a
one-line registration. When the operation should read like a method, use
`functools.singledispatchmethod` instead.

Visitor still has a place: when you truly cannot define functions over the
hierarchy, or you need the `accept()` hook for some other reason. But in Python
that is rare. As with [the Pattern Refactoring chapter](30_Pattern_Refactoring.md)'s price-and-weight
example, `singledispatch` is the open-method mechanism Visitor was invented to
fake.

## Verifying the Operations

Because each operation is a plain function, testing is direct: call it with each
flower type and assert the result. The cases worth covering are the registered
types, the `@singledispatch` default for an unregistered type, and the fact that
the two operations dispatch independently:

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
    # nectar knows Gladiolus and Chrysanthemum; fragrance knows
    # Runuculus. A Runuculus falls to nectar's default but hits
    # fragrance's registered case.
    runuculus = Runuculus()
    assert nectar(runuculus) == "Runuculus: no nectar"
    assert fragrance(runuculus) == "strong"
```

## Exercises

1.  Create a business-modeling environment with three types of
    `Inhabitant`: `Dwarf` (for engineers), `Elf` (for marketers)
    and `Troll` (for managers). Now create a class called `Project`
    that creates the different inhabitants and causes them to
    `interact()` with each other using multiple dispatching.
2.  Modify the above example to make the interactions more detailed.
    Each `Inhabitant` can randomly produce a `Weapon` using
    `getWeapon()`: a `Dwarf` uses `Jargon` or `Play`, an
    `Elf` uses `InventFeature` or `SellImaginaryProduct`, and a
    `Troll` uses `Edict` and `Schedule`. You must decide which
    weapons "win" and "lose" in each interaction (as in
    `paper_scissors_rock.py`). Add a `battle()` method to
    `Project` that takes two `Inhabitant`s and matches them against
    each other. Now create a `meeting()` method for
    `Project` that creates groups of `Dwarf`, `Elf` and `Troll`
    and battles the groups against each other until only members of one
    group are left standing. These are the "winners."
3.  Modify `paper_scissors_rock.py` to replace the double dispatching
    with a table lookup. The easiest way to do this is to create a
    `Map` of `Map`s, with the key of each `Map` the class of each
    object. Then you can do the lookup by saying:
    ((Map)map.get(o1.getClass())).get(o2.getClass()) Notice how much
    easier it is to reconfigure the system. When is it more appropriate
    to use this approach vs. hard-coding the dynamic dispatches? Can you
    create a system that has the syntactic simplicity of use of the
    dynamic dispatch but uses a table lookup?
4.  Modify Exercise 2 to use the table lookup technique described in
    Exercise 3.
