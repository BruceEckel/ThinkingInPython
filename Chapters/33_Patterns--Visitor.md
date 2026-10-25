# Visitor

> A family of classes you cannot change needs a new operation.
> *Visitor* adds the operation from outside the family.

The *Visitor* pattern uses [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md).
People can confuse the two by looking at the implementation rather than the intent.

*Visitor* assumes you have a primary class hierarchy you cannot change,
perhaps because it comes from another vendor.
You'd like to add new polymorphic methods to it,
which normally means declaring them in the base class interface.
How do you add them from outside the base class?

## The Classic Visitor

*Visitor*, the final pattern in *GoF Design Patterns*,
requires one method on the primary class hierarchy, typically called `accept()`,
which takes an object from a secondary hierarchy called `Visitor`.
`accept()` calls the visitor's `visit()`, passing `self`.
The visitor's type chooses which `visit()` runs.

The `accept()` requirement limits where *Visitor* applies.
The hierarchy's author must write `accept()` in advance,
because you cannot add it to a vendor's classes yourself.

Here, bugs visit flowers:

```python
# flower_visitors.py
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
```

A new `Visitor` subclass such as `Fly` reuses an existing operation,
so it leaves the primary hierarchy as it is.
In this Python form of the pattern,
a new operation whose behavior varies by flower type also needs a new method on `Flower`.
[Two Departures from the Classic Shape](#two-departures-from-the-classic-shape)
explains why.

Each flower accepts each bug in turn:

```python
# bug_visits.py
from flower_visitors import (Bee, Chrysanthemum, Fly,
                             Gladiolus, Ranunculus, Worm)

bee = Bee()
fly = Fly()
worm = Worm()
for flower in (Gladiolus(), Ranunculus(), Chrysanthemum()):
    flower.accept(bee)
    flower.accept(fly)
    flower.accept(worm)
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

In the classic pattern the `accept()`/`visit()` pair is the double dispatch.
Every element class overrides `accept()`,
the override resolves the element's type,
and the `visit()` call inside it resolves the visitor's type.
In `flower_visitors.py` one inherited `accept()` passes the concrete flower to the visitor,
`visit()` resolves the visitor's type,
and the `pollinate()` or `eat()` call inside `visit()` resolves the flower's type a step later.

In the last line of `bug_visits.py`'s output, both dispatches change the result,
because `Chrysanthemum` overrides `eat()`
(chrysanthemums really do produce a natural insecticide).
The worm's type chooses `eat()`,
and the flower's type chooses which `eat()` runs.
If you delete the override, every flower resolves to the same `Flower.eat()`,
so the visitor's type alone decides which method runs.

`bug_visits.py`'s output shows results, not mechanism.
Printing the qualified name of the method to which each dispatch resolves makes both dispatches visible:

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

The first dispatch resolves to `Predator.visit` rather than `Worm.visit`,
because `Worm` inherits the operation from the class that defines it.

## Two Departures from the Classic Shape

One annotation in `flower_visitors.py` looks like a shortcut,
but the empty base class requires it.
`accept()` types its visitor as `Any` because the `Visitor` base class declares no `visit()` method.
If you declare that parameter as `Visitor` instead,
the type checker reports `visitor.visit` as an unresolved attribute.
The classic pattern declares `visit()` abstract on the visitor base,
so `visitor.visit` resolves.
A [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
that declares `visit()` removes the `Any`:

    class Visits(Protocol):
        def visit(self, flower: Flower) -> None: ...

    class Flower:
        def accept(self, visitor: Visits) -> None:
            visitor.visit(self)

`flower_visitors.py` keeps the empty `Visitor` base and the `Any` in `accept()`,
to show what the `Any` gives up: every check on the visitor side.
`Gladiolus().accept(Bug())` passes the type checker and fails at runtime with `AttributeError: 'Bug' object has no attribute 'visit'`.
In [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#two-dispatches-through-methods),
the `Any` in `paper_scissors_rock.py` lets a class that omits an `eval_*()` method pass the checker and raise an `AttributeError` at runtime.
The `Any` in `accept()` is a choice,
unlike the one in [Data Transfer Objects](28_Patterns--Data_Transfer_Objects.md#a-hand-rolled-messenger),
where a bag of attributes named at runtime leaves no precise type to write.

The classic pattern overloads `visit()` once per flower type and keeps each operation's body in the visitor,
so `accept()` is the one method the pattern adds to the primary hierarchy.
Python has no method overloading,
since a second `def visit()` replaces the first.
[`@overload`](20_Patterns--Rethinking_Objects.md#what-is-polymorphism)
declares extra signatures for the type checker and leaves the runtime with one implementation,
which must branch on the argument's type.
`flower_visitors.py` therefore puts the type-specific behavior in `pollinate()` and `eat()` on the flowers.
The visitors choose between those two methods.
So `flower_visitors.py`'s primary hierarchy holds the operations the pattern exists to keep out of it.

A Python visitor can keep the operations in its own methods by building the method name from the element's class,
as `ast.NodeVisitor` does.
Its `visit()` calls `getattr(self, "visit_" + node.__class__.__name__, self.generic_visit)`,
so a node class with no matching method falls back to `generic_visit()`.
The type checker cannot resolve a method name built from a string at runtime.

## The Pythonic Visitor: singledispatch

`functools.singledispatch` adds an operation to an existing hierarchy from outside,
as *Visitor* does, but without the `accept()` method or the `Visitor` class hierarchy.
`singledispatch` turns a plain function into one that dispatches on the type of its first argument,
with per-type implementations registered from anywhere.
Here, the flowers are the same three as in `flower_visitors.py`.
The two operations, `nectar()` and `fragrance()`, are new,
each added independently of the other:

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
    for flower in flowers:
        print(nectar(flower), "| fragrance:",
              fragrance(flower))
#: Gladiolus: abundant nectar | fragrance: faint
#: Ranunculus: no nectar | fragrance: strong
#: Chrysanthemum: a little nectar | fragrance: faint
```

Both operations live outside `Flower`, which stays as it is.

`@nectar.register` reads the annotation on the implementation's first parameter.
For `flower: Gladiolus`,
it stores that implementation in the dispatch table under the key `Gladiolus`.
A union annotation, `flower: Gladiolus | Ranunculus`,
registers one implementation for several types at once.

A registered implementation's name can be anything,
since a call to `nectar()` finds that implementation through the dispatch table.
`_` is the conventional placeholder for a name that exists only to satisfy `def`.
Reusing `_` for every registration is safe.
`@nectar.register` stores the function in its dispatch table before the next `def _` rebinds the name,
so every implementation stays in the table.

Dispatch follows inheritance.
A subclass resolves to its nearest registered ancestor.
`@singledispatch` registers the base implementation under `object`,
from which every class descends.
A type whose only registered ancestor is `object` therefore gets the default.

`nectar()` exposes the dispatch table the decorator built:

```python
# dispatch_table.py
from visitor_singledispatch import Ranunculus, nectar

print(sorted(cls.__name__ for cls in nectar.registry))
#: ['Chrysanthemum', 'Gladiolus', 'object']
print(nectar.dispatch(Ranunculus)
      is nectar.registry[object])
#: True
```

`nectar.registry` maps each registered type to its implementation.
`nectar.dispatch(cls)` reports the implementation to which `cls` resolves.
Nothing registers `Ranunculus`,
so `Ranunculus` resolves to the same implementation `Flower` does,
the one stored under `object`.

A new `Flower` subclass gets the default answer until someone registers it.
Both the runtime and the checker accept the `nectar()` call on that subclass,
so a forgotten registration returns the default's `no nectar` string and raises no exception.

The default also accepts arguments outside `Flower`.
Because the default sits under `object`,
not under the `Flower` in its annotation, `nectar(42)` returns `42: no nectar`.
`ty` and Pyright accept `nectar(42)` too,
because the dispatcher that `@singledispatch` builds declares its parameters as `Any`.
Only mypy rejects it,
since mypy's built-in `singledispatch` plugin checks the call against the base function's signature.

When the default answer is wrong for an unregistered type,
give the base function a `raise NotImplementedError(f"no nectar rule for {type(flower).__name__}")` in place of the fallback string.
A forgotten registration then fails at its first call.
A `match` over a union of types goes further when `assert_never()` sits in its `case _`.
The type checker [reports the omission](34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes)
before anything runs.
The set of types is then closed, since adding a type means editing the union.

Under `@singledispatch`, adding a new operation is a new function.
Adding a new flower is a class,
plus one registration for each operation whose default answer is wrong for it.

When the operation should be a method of a class,
use [`functools.singledispatchmethod`](41_Functional--Toolkits.md#singledispatchmethod)
instead.
`singledispatchmethod` dispatches on the first argument after `self`.

### Testing the Operations

Because each operation is a plain function,
a test calls it with each flower type and asserts the result.
The tests cover the registered types,
the `@singledispatch` default for an unregistered type,
and a subclass that resolves to its nearest registered ancestor:

```python
# test_visitor.py
import pytest
from visitor_singledispatch import (Chrysanthemum, Flower,
                                    Gladiolus, Ranunculus,
                                    fragrance, nectar)

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
    (Flower(), "faint"),
])
def test_fragrance_registered_and_default(
    flower: Flower, expected: str
) -> None:
    assert fragrance(flower) == expected

def test_dispatch_follows_inheritance() -> None:
    class Hybrid(Gladiolus):
        pass

    assert Hybrid not in nectar.registry
    assert nectar(Hybrid()) == "Hybrid: abundant nectar"
```

## Where Visitor Still Fits

*Visitor* still has a place:
when an object must loop over its own elements inside `accept()`,
or when someone else's framework calls that method.
Both cases are rare in Python.
[Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#one-singledispatch-function-per-operation)
draws the same conclusion from its `recycling_note.py` example.

A minimal example shows the first of those cases,
a loop that runs inside `accept()`:

```python
# recursive_accept.py
from typing import Any, Protocol
from flower_visitors import Bee, Gladiolus, Ranunculus, Worm

class Accepts(Protocol):
    def accept(self, visitor: Any) -> None: ...

# accept() drives the traversal itself:
class Corsage:
    def __init__(self, *elements: Accepts) -> None:
        self.elements = elements

    def accept(self, visitor: Any) -> None:
        for element in self.elements:
            element.accept(visitor)

if __name__ == "__main__":
    corsage = Corsage(
        Gladiolus(), Corsage(Ranunculus()))
    for bug in (Bee(), Worm()):
        corsage.accept(bug)
#: Gladiolus pollinated by Bee
#: Ranunculus pollinated by Bee
#: Gladiolus eaten by Worm
#: Ranunculus eaten by Worm
```

The recursion works because `Corsage` and `Flower` both define `accept()`.
The loop in `Corsage.accept()` makes the same call, `element.accept(visitor)`,
on each element, whether the element is a flower or another corsage.
The `Accepts` protocol declares that shared method,
so the type checker reports an element that lacks `accept()`,
such as `Corsage("rose")`, before the program runs.

In `bug_visits.py` the loop that calls `accept()` sits outside the hierarchy,
at module level, and takes one flower at a time from a tuple.
In `recursive_accept.py` the loop runs inside `accept()`,
the situation where the classic pattern still fits.
Every visitor reuses that one loop.
A new visitor defines `visit()` for a single flower.
`Corsage.accept()` passes that visitor to every nested element.

## One Dispatch Is Enough

*Visitor* dispatches twice.
`singledispatch` dispatches once.
The figure sets *Visitor* and `singledispatch` side by side,
with the worm from `dispatch_trace.py` and the `nectar()` operation from `visitor_singledispatch.py`:

![](_images/visitor_story)

In the first two frames `Flower.accept()` calls `visit()` on the worm,
outside `Flower`, and `Predator.visit()` calls `eat()` back on the flower.
The frames differ only in which `eat()` that second call reaches.
In the third frame no method on `Flower` takes part.
`nectar()`'s table, keyed by the flower's type,
yields the implementation in one lookup.
That one dispatch resolves everything *Visitor*'s two dispatches do.

The dispatch on the visitor's type exists not because two types are unknown,
but because the operation must be a method on some class.
The visitor's type chooses the operation,
so the language must resolve that type at runtime along with the flower's type.
When an operation can be a function defined outside the hierarchy,
the call site names the operation,
so writing `nectar()` rather than `fragrance()` selects it before the program runs.
The flower's type is the one thing left for runtime to resolve.
One dispatch covers it.

*Visitor* adds operations to a hierarchy you cannot edit,
and its double dispatch is the means.
*Multiple Dispatching* is the end in itself.
Two objects must interact, and both their types stay unknown until runtime,
as in `paper_scissors_rock.py`.
`singledispatch` resolves one argument's type.
The *Multiple Dispatching* problem needs two.
When both types must resolve together at runtime,
use the table from [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-type-or-many),
keyed by a tuple of types.

## Exercises

Try each exercise before opening its [solution](../Solutions/33_Patterns--Visitor/).

1.  Rewrite `flower_visitors.py` with `singledispatch`.
    Make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
    with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
    Which classes and which methods disappear?
2.  Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
    then add a third operation, `thorns()`, over all four flowers.
    Count the lines each change adds,
    and say which of the two changes `@singledispatch` makes shorter.
3.  Rewrite `flower_visitors.py` with the `Visits` protocol in place of `Any`,
    so `accept()` declares what it needs.
    Then add a `Beetle(Bug)` with no `visit()` method and pass it to `accept()`.
    Which version reports the mistake, and when?
