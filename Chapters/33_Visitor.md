# Visitor

The *Visitor* pattern uses *Multiple Dispatching*.
People can confuse the two by looking at the implementation rather than the intent.

*Visitor* assumes you have a primary class hierarchy you cannot change.
Perhaps it's from another vendor and you can't touch its source.
However, you'd like to add new polymorphic methods to it.
Normally you'd add something to the base class interface,
but that's not an option.
How do you get around this?

*Visitor*, the final pattern in *GoF Design Patterns*,
solves this kind of problem.
It lets you extend the interface of the primary class hierarchy.
It requires that the primary class hierarchy have a method,
typically called `accept()`,
which takes an object of a secondary class hierarchy called `Visitor`.
The operations on the primary hierarchy become dynamically bound.
The objects of the primary hierarchy `accept()` the `Visitor`,
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
        return type(self).__name__

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
        return type(self).__name__

class Bug(Visitor):
    pass

# The middle layer names the operation:
class Pollinator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

class Predator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.eat(self)

# Concrete visitors, grouped by the operation they perform:
class Bee(Pollinator):
    pass
class Fly(Pollinator):
    pass
class Worm(Predator):
    pass

def flower_gen(n: int) -> Iterator[Flower]:
    flowers = Flower.__subclasses__()
    for _ in range(n):
        yield random.choice(flowers)()

# Now perform Bug operations on the flowers:
if __name__ == "__main__":
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
which resolves the element's type; here one inherited `accept()` is enough,
because the flower's type resolves a step later.
The last line of output shows both dispatches doing visible work.
`Chrysanthemum` overrides `eat()`
(chrysanthemums really do produce a natural insecticide),
so that line depends on both unknown types at once:
the worm's type chooses `eat()`,
and the flower's type chooses which `eat()` runs.
If you delete the override, the program still runs;
the flower-side dispatch goes back to having nothing to say.

The output above shows results, not mechanism.
Printing the qualified name of the method each hop reaches makes the pair visible:

```python
# dispatch_trace.py
from flower_visitors import Chrysanthemum, Gladiolus, Worm

worm = Worm()
for flower in (Chrysanthemum(), Gladiolus()):
    print(type(worm).visit.__qualname__,
          "then", type(flower).eat.__qualname__)
    flower.accept(worm)
#: Predator.visit then Chrysanthemum.eat
#: Chrysanthemum is toxic to Worm
#: Predator.visit then Flower.eat
#: Gladiolus eaten by Worm
```

The first hop reaches `Predator.visit` rather than `Worm.visit`,
because `Worm` inherits the operation from the class that defines it.
For `Chrysanthemum` the second hop reaches the override,
and for `Gladiolus` it reaches `Flower.eat`:
the flower-side dispatch has nothing to say, and the output now shows it.

## The Price of the Empty Base

One annotation in `flower_visitors.py` looks like a shortcut and is not.
`accept()` types its visitor as `Any` because the `Visitor` base class declares no `visit()` method:
declaring that parameter as `Visitor` instead fails the type checker.
The classic pattern fixes this by declaring `visit()` abstract on the visitor base.
A `Protocol` removes the `Any` for two new lines and an import:

    class Visits(Protocol):
        def visit(self, flower: Flower) -> None: ...

    class Flower:
        def accept(self, visitor: Visits) -> None:
            visitor.visit(self)

The chapter keeps `Any` because the empty `Visitor` base is what the classic pattern looks like,
and seeing the price is part of the point.
The price is that nothing checks the visitor side:
`Gladiolus().accept(Bug())` passes the type checker and fails at runtime with `AttributeError: 'Bug' object has no attribute 'visit'`.
That is the same gap the `Any` in `paper_scissors_rock.py` leaves in [Multiple Dispatching](32_Multiple_Dispatching.md).
This `Any` is a choice,
unlike the one in [Data Transfer Objects](22_Data_Transfer_Objects.md),
where a bag of attributes named at runtime leaves no precise type to write.

Notice where the behavior lives.
The classic pattern overloads `visit()` once per flower type and keeps each operation's body in the visitor,
so it adds only `accept()` to the primary hierarchy.
Python has no method overloading,
since a second `def visit()` replaces the first,
so this version puts the type-specific behavior in `pollinate()` and `eat()` on the flowers instead,
and the visitors choose between them.
Whichever way you write it,
the primary hierarchy ends up carrying code the pattern exists to keep out of it.

## The Pythonic Visitor: singledispatch

Python can add a method to a fixed hierarchy from outside,
using `functools.singledispatch`.
It turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
That is what *Visitor* does,
without the `accept()` method or the `Visitor` class hierarchy.
The flowers below are the same three.
The two operations are new, each added independently of the other:

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
    print(sorted(t.__name__ for t in nectar.registry))
    print(nectar.dispatch(Ranunculus)
          is nectar.dispatch(Flower))
#: Gladiolus: abundant nectar | fragrance: faint
#: Ranunculus: no nectar | fragrance: strong
#: Chrysanthemum: a little nectar | fragrance: faint
#: ['Chrysanthemum', 'Gladiolus', 'object']
#: True
```

`@nectar.register` reads the annotation on the implementation's first parameter:
`flower: Gladiolus` files that implementation under `Gladiolus`.
A union annotation, `flower: Gladiolus | Ranunculus`,
registers one implementation for several types at once.
Each registered implementation takes the name `_`.
`nectar()` calls it through the dispatcher, not by its own name,
so the name carries no meaning.
`_` is the conventional placeholder for a name nobody uses.
Reusing `_` for every registration is safe:
`@nectar.register` stores the function in its dispatch table before the next `def _` rebinds the name,
so nothing goes missing.

Nothing touches `Flower`.
Each operation is a separate function,
and the `@singledispatch` default handles any type you have not registered.
Dispatch follows inheritance:
an unregistered subclass uses its nearest registered ancestor,
falling back to the base implementation only when no registered ancestor exists
(the tests below pin this down).

The listing's last two output lines print the dispatch table the decorator built.
`nectar.registry` maps each registered type to its implementation,
and `nectar.dispatch(cls)` reports the implementation to which `cls` resolves.
Nothing registers `Ranunculus`,
so it resolves to the same implementation `Flower` does,
the one filed under `object`.

The default is also the risk.
A new `Flower` subclass that nobody registers gets the default answer with no exception and no static complaint,
so a forgotten registration shows up as a wrong result rather than a failure.
The default reaches further than `Flower`, too:
`@singledispatch` registers the base implementation under `object`,
not under the `Flower` in its annotation,
so `nectar(42)` returns `42: no nectar`.
The type checker does not object either,
because the dispatcher it builds declares its parameters as `Any`.
When no sensible answer exists for an unregistered type,
give the base function a `raise NotImplementedError(f"no nectar rule for {type(flower).__name__}")` instead of a fallback string.
The omission then fails at the first call.
A `match` over a closed union of types, with `assert_never()` in the `case _`,
goes further and lets the type checker catch it instead
([Composite and Interpreter](34_Composite_and_Interpreter.md#a-composite-of-data-classes)),
at the price of a set of types no one else can extend.
Adding a new operation is a new function.
Adding a new flower is a class,
plus one registration for each operation that needs more than the default.
When the operation should read like a method,
use [`functools.singledispatchmethod`](41_Functional_Toolkits.md#singledispatchmethod)
instead, which dispatches on the first argument after `self`.

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

@pytest.mark.parametrize("flower, expected", [
    (Gladiolus(), "Gladiolus: abundant nectar"),
    (Chrysanthemum(), "Chrysanthemum: a little nectar"),
    (Ranunculus(), "Ranunculus: no nectar"),
    (Flower(), "Flower: no nectar"),
])
def test_nectar_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert nectar(flower) == expected

@pytest.mark.parametrize("flower, expected", [
    (Ranunculus(), "strong"),
    (Gladiolus(), "faint"),
    (Chrysanthemum(), "faint"),
])
def test_fragrance_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert fragrance(flower) == expected

def test_dispatch_follows_inheritance() -> None:
    # Unregistered: the nearest registered ancestor wins
    class Hybrid(Gladiolus):
        pass

    assert nectar(Hybrid()) == "Hybrid: abundant nectar"
```

*Visitor* still has a place:
when the elements must drive the traversal themselves from inside `accept()`,
or when a framework you do not own already calls that method.
But in Python that is rare.
As with [Pattern Refactoring](37_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)'s recycling-note example,
`singledispatch` is the open-method mechanism that *Visitor* fakes.

## One Dispatch Is Enough

*Visitor* dispatches twice, and `singledispatch` dispatches once.
The trade loses nothing.
The second dispatch in the classic pattern exists not because two types are unknown,
but because the operation has nowhere else to live.
The visitor's type stands in for the operation,
so the language must resolve it at runtime along with the element's type.
Once an operation can be a function defined outside the hierarchy,
calling `nectar()` instead of `fragrance()` selects the operation before anything runs,
and only the flower's type is still unknown.
One dispatch covers it.

That is the intent difference from the chapter's opening.
*Visitor* adds operations to a hierarchy you cannot edit,
and its double dispatch is the means.
*Multiple Dispatching* is the end in itself:
two objects whose types are both unknown until runtime must interact,
as in `paper_scissors_rock.py`.
`singledispatch` dispatches on the first argument only,
so it does nothing for that second problem.
When two types must genuinely resolve together,
use the table keyed by a tuple of types from [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many).

## Exercises

1.  Rewrite `flower_visitors.py` with `singledispatch`:
    make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
    with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
    Which classes and which methods disappear?
2.  Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
    then add a third operation, `thorns()`, over all four flowers.
    Count the lines each change costs,
    and say which of the two `@singledispatch` makes cheaper.
3.  Rewrite `flower_visitors.py` with the `Visits` protocol in place of `Any`,
    so `accept()` declares what it needs.
    Then add a `Beetle(Bug)` with no `visit()` method and pass it to `accept()`.
    Which version reports the mistake, and when?
