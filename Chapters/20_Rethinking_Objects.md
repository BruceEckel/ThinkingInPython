# Rethinking Objects

I spent much of my career promoting objects.
I wrote *Thinking in C++* and *Thinking in Java*,
served on the C++ Standards Committee for its first eight years,
and toured the world giving object-oriented programming (OOP) presentations.
When I say I have come to doubt that objects should be the default,
it is not an outsider's complaint.

This section is about design patterns, most of which assume objects and inheritance.
First, however, I want to question how much of that machinery we actually need.
This chapter adapts my PyCon 2023 talk,
[Rethinking Objects](https://github.com/BruceEckel/RethinkingObjects),
and my StrangeLoop presentation [Polymorphism Unbound](https://github.com/BruceEckel/PolymorphismUnbound).

## Evolution

Languages evolve to fit their environment.
A feature that looks strange now usually made sense for the problem,
and the hardware, of its time.
Consider the origin of OOP.

*Simula* introduced objects in the 1960s to model simulations:
a system is a set of things that interact.
Notably, not everything in Simulat was an object; the language still had standalone functions.
It was a compiled, statically typed language,
so the discipline later named the Liskov Substitution Principle (LSP) fit naturally.

*Smalltalk* took the other road: everything is an object,
and the only thing you do is send messages to objects, always late-bound.
It was an emphatically dynamic,
run-time world where you built programs by finding the closest existing object and inheriting from it to add behavior.
That style makes no substitutability promises.

*C++* drew from Simula.
Objects were optional, and it brought object-oriented programming and exceptions into the mainstream.

*Java* drew from Smalltalk.
Everything lives inside a class, even when all you need is a function.
Java is statically compiled, so substitutability matters,
yet it encouraged reusing code by inheriting implementation,
which pulls in the other direction.

Newer languages backed away from inheritance.
Rust, Swift, Go, and Kotlin lean on data structures over deep class hierarchies.
They favor immutability.
Rust makes bindings immutable by default.
Swift and Kotlin encourage immutability through `let` and `val`
(Go has no general immutability).
They compose data structures instead of inheriting implementation,
and they let code live outside classes, which cuts duplication.
The industry has been quietly walking back from "everything is an object" and from implementation inheritance.

## The Liskov Substitution Principle {#liskov-substitution}

The *Liskov Substitution Principle* (LSP)
says that an object of a subtype must work anywhere code expects an object of its base type,
without breaking the program.
A subclass may add behavior, but it must honor the base class's contract.
It accepts the same arguments, returns the same kinds of results,
and raises no surprising exceptions.
When subclasses obey it,
code written against the base class works unchanged on any of them.
This is the guarantee that makes polymorphism,
and patterns like the [Template Method](25_Template_Method.md), safe.
The base class calls a method and trusts every subclass to stand in for it.
The rest of this chapter shows why.

## Encapsulation Leaks

The first OOP promise is encapsulation: hide the data,
expose it only through methods you control.
In Python the usual move is a leading underscore and a read-only property.
It does not work as well as it looks.
A getter that returns a mutable object hands the caller a reference to the real internals:

```python
# leaky.py
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Leaky:
    def __init__(self, numbers: list[int]) -> None:
        self._numbers = numbers  # "Private" by convention
        self._bob = Bob()

    @property
    def numbers(self) -> list[int]:
        return self._numbers

    @property
    def bob(self) -> Bob:
        return self._bob

if __name__ == "__main__":
    leaky = Leaky([1, 2])
    print(leaky.numbers is leaky._numbers)  # The same object
    # Both mutate the "private" internals through the getters:
    leaky.numbers.append(999)
    leaky.bob.name = "Ralph"
    print(leaky.numbers, leaky.bob)
#: True
#: [1, 2, 999] Bob(name='Ralph')
```

Encapsulation with private fields and getters still leaks.
The `is` check shows the mechanism:
the getter does not return a view or a snapshot of the list,
it returns the list, the identical object the underscore was hiding.
Python's `return` hands out references, never copies.
The property blocked reassigning `numbers`,
but it could not stop the caller from mutating the list it returned.

Testing shows the leak:

```python
# test_leaky.py
from leaky import Leaky

def test_getter_leaks_internal_state() -> None:
    leaky = Leaky([1, 2])
    leaky.numbers.append(999)  # Changes the internal list
    assert leaky.numbers == [1, 2, 999]
```

Mutating the returned list manipulates the internal state.

## Plugging the Leaks Is Tedious

You can stop the leak by copying everything a getter returns.
It works, but every getter must remember to do it,
and so does every getter in every subclass, forever:

```python
# plugged.py
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class Bob:
    name: str = "Bob"

class Plugged:
    def __init__(self, numbers: list[int]) -> None:
        self._numbers = numbers
        self._bob = Bob()

    @property
    def numbers(self) -> list[int]:
        return self._numbers.copy()  # Hand back a copy, not our list

    @property
    def bob(self) -> Bob:
        return deepcopy(self._bob)

if __name__ == "__main__":
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates a copy, not ours
    plugged.bob.name = "Ralph"  # Ditto
    print(plugged.numbers, plugged.bob)
#: [1, 2] Bob(name='Bob')
```

Now the internals are safe, but look at what we are doing.
We add private fields, getters, and defensive copies,
all to stop other code from changing our data.
And these copies plug only the outbound leak.
The constructor stored the caller's own list,
so the caller's original reference still mutates the internals.
A fully defensive class must copy on the way in as well.

The two getters also copy differently, and the difference is its own trap.
`list.copy()` is *shallow*: it duplicates the container but shares the elements,
which is safe here only because the elements are immutable `int`s.
`Bob` gets `deepcopy()`,
which recursively copies everything the object references,
the conservative choice when a field's own fields might be mutable.
A shallow copy of a list of `Bob`s would plug nothing:
the caller's copy of the list would still hold your actual `Bob`s.

Testing confirms the defensive copy holds.
Mutating the returned list leaves the original untouched:

```python
# test_plugged.py
from plugged import Plugged

def test_defensive_copy_prevents_the_leak() -> None:
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates only a copy
    assert plugged.numbers == [1, 2]
```

## The Immutability Solution

Encapsulation exists only because of mutability.
If the data cannot change, there is nothing to protect.
Freeze it, and the whole apparatus disappears.
The fields are public, there are no getters, and there are no copies:

```python
# immutable.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Bob:
    name: str = "Bob"

@dataclass(frozen=True)
class Immutable:
    numbers: tuple[int, ...]
    bob: Bob

if __name__ == "__main__":
    immutable = Immutable((1, 2), Bob())
    print(immutable)
    # immutable.numbers is a tuple, so it has no append.
    # immutable.bob.name = "Ralph" raises FrozenInstanceError.
#: Immutable(numbers=(1, 2), bob=Bob(name='Bob'))
```

The frozen object refuses mutation:

```python
# test_immutable.py
import dataclasses
import pytest
from immutable import Bob, Immutable

def test_frozen_cannot_be_mutated() -> None:
    immutable = Immutable((1, 2), Bob())
    with pytest.raises(dataclasses.FrozenInstanceError):
        # Frozen, so the assignment fails:
        setattr(immutable.bob, "name", "Ralph")
```

Two quiet changes in the listing do as much work as `frozen=True`,
and it pays to notice them.
`frozen=True` is shallow:
it stops assignment to the fields of `Immutable` itself,
but it cannot stop mutation inside a field that is itself mutable.
Declare the field as a `list` instead and the leak reopens:

```python
# frozen_leaky.py
from dataclasses import FrozenInstanceError, dataclass

@dataclass(frozen=True)
class FrozenLeaky:
    numbers: list[int]  # A mutable field in a frozen class

fl = FrozenLeaky([1, 2])
fl.numbers.append(999)  # frozen=True does not stop this
print(fl.numbers)
#: [1, 2, 999]
try:
    fl.numbers = []  # type: ignore
except FrozenInstanceError as e:
    print(type(e).__name__)
#: FrozenInstanceError
```

Frozen guards the binding, not the object.
`fl.numbers` must keep pointing at the same list, and rebinding it raises,
but nothing stops that list from changing, the identical leak `Leaky` had.
That is why `numbers` became a `tuple` and why `Bob` froze too.
Immutability pays off only when it goes all the way down.

[Data Classes as Types](12_Data_Classes_as_Types.md#immutability)
makes the case for frozen data classes.
Most encapsulation is only necessary because you allowed mutation in the first place.

## Methods or Functions?

The second OOP promise is that behavior belongs inside the object, as methods.
But a method is only a function whose first argument is the object.
Compare a method with a function that does the same thing:

```python
# point_distance.py
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:  # As a method
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

def distance(a: Point, b: Point) -> float:  # As a free function
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

if __name__ == "__main__":
    p1, p2 = Point(3, 0), Point(0, 4)  # A 3-4-5 right triangle
    print(p1.distance_to(p2))
    print(Point.distance_to(p1, p2))  # The method, as a function
    print(distance(p1, p2))
#: 5.0
#: 5.0
#: 5.0
```

The middle call is the claim made concrete.
Fetched from the class instead of from an instance,
`distance_to` is an ordinary function,
and `p1` is passed to it as the first argument.
`p1.distance_to(p2)` is shorthand for exactly that call;
the dot fills in `self`, nothing more.
The function reads the same and computes the same.
The class does not need to own it.
The function is not worse, and it has an advantage.
It need not live inside `Point`.

Testing confirms the method and the free function agree:

```python
# test_point_distance.py
from point_distance import Point, distance

def test_method_and_function_agree() -> None:
    p1, p2 = Point(3, 0), Point(0, 4)
    assert p1.distance_to(p2) == 5
    assert distance(p1, p2) == 5
```

## Protocols Generalize, Composition Adapts

Because the function does not belong to a class,
it can work on anything shaped like a point.
A `Protocol` describes that shape,
and any type with the right attributes satisfies it,
with no declared inheritance.
This is the structural typing from [Static Typing](08_Static_Typing.md#structural-typing-with-protocols).
When someone hands you a type that does not fit, you adapt it by composition,
not inheritance:

```python
# distance_protocol.py
from dataclasses import dataclass
from math import sqrt
from typing import Protocol

class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

def distance(a: Coord, b: Coord) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass(frozen=True)
class Pair:  # Suppose you are handed this, with no x or y
    a: float
    b: float

@dataclass(frozen=True)
class PairCoord:  # An adapter built by composition, not inheritance
    pair: Pair

    @property
    def x(self) -> float:
        return self.pair.a

    @property
    def y(self) -> float:
        return self.pair.b

if __name__ == "__main__":
    print(distance(Point(3, 0), Point(0, 4)))
    print(distance(PairCoord(Pair(3, 0)), PairCoord(Pair(0, 4))))
#: 5.0
#: 5.0
```

`Point` and `PairCoord` share no base class.
They both have `x` and `y`, which is all `distance()` required.

Testing confirms `distance()` works on both a `Point` and an adapted `Pair`:

```python
# test_distance_protocol.py
import distance_protocol as dp

def test_protocol_and_adapter() -> None:
    assert dp.distance(dp.Point(3, 0), dp.Point(0, 4)) == 5
    assert dp.distance(dp.PairCoord(dp.Pair(3, 0)),
                       dp.PairCoord(dp.Pair(0, 4))) == 5
```

## Compose, Do Not Inherit

The third OOP promise is reuse through inheritance.
In practice, inheriting implementation couples a subclass to its base in ways that are hard to undo.
The alternative is composition.
A type holds other types as fields.
`dataclasses.replace()` gives you the copy-with-changes that immutability needs,
and frozen instances compare by value and work as keys:

```python
# composition.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Name:
    first: str
    last: str

@dataclass(frozen=True)
class Address:
    city: str
    postal: str

@dataclass(frozen=True)
class Contact:  # A Contact has a Name and an Address
    name: Name
    address: Address

c = Contact(
    Name("Bruce", "Eckel"), Address("Crested Butte", "81224"))
print(c.name)
#: Name(first='Bruce', last='Eckel')
print(c.address)
#: Address(city='Crested Butte', postal='81224')

# A copy with one nested field changed leaves c intact
moved = replace(c, address=replace(c.address, city="Carbondale"))
print(c.address.city, "->", moved.address.city)
#: Crested Butte -> Carbondale

twin = Contact(
    Name("Bruce", "Eckel"), Address("Crested Butte", "81224"))
print(c == twin)  # Value equality, field by field
#: True
print({c: "value"}[c])  # Hashable, so it works as a dict key
#: value
```

## Polymorphism Without Inheritance

The fourth OOP promise is polymorphism.
This is usually taught through inheritance, but that is only one form.
More broadly, polymorphism means a function parameter accepts more than one type.
The questions are which types it accepts,
and what the function may do with them.

The classic object-oriented answer uses an abstract base class.
The base type names both the allowed types, its subclasses,
and what you may do with them, its methods:

```python
# shapes_oo.py
import math
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, length: float, width: float) -> None:
        self.length = length
        self.width = width

    @override
    def area(self) -> float:
        return self.length * self.width

class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @override
    def area(self) -> float:
        return math.pi * self.radius**2

if __name__ == "__main__":
    for shape in [Circle(1.0), Rectangle(3.0, 4.0)]:
        print(round(shape.area(), 4))
#: 3.1416
#: 12.0
```

Inheriting from `ABC` makes `Shape` abstract.
You cannot instantiate it,
and `@abstractmethod` forces every subclass to define `area()`.

Dynamic typing produces a different approach.
Any type works as long as it has the method the function calls.
No shared base class or declared set of types exists,
and the only validity check happens at runtime, when the call runs:

```python
# dynamic_typing.py
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Bicycle:
    id: str

    def display(self) -> str:
        return f"Bicycle {self.id}"

@dataclass(frozen=True)
class Glider:
    size: int

    def display(self) -> str:
        return f"Glider {self.size}"

def show(t: Any) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
#: Bicycle Bob
#: Glider 65
```

`show()` accepts anything.
Pass it something without a `display()` method and you find out only when the line runs.
The annotation is doing that, and `Any` is not `object`.
Annotated `t: object`, the safe top type, `show()` would fail the type checker,
because `object` has no `display()` method.
`Any` instead switches the checker off for `t`, permitting every operation.
It is dynamic typing opted into, one parameter at a time.
[Static Typing](08_Static_Typing.md#structural-typing-with-protocols)
gives this a static form with `Protocol`:

```python
# protocols_typed.py
from dataclasses import dataclass
from typing import Protocol

class Displayable(Protocol):
    def display(self) -> str: ...

@dataclass(frozen=True)
class Bicycle:
    id: str

    def display(self) -> str:
        return f"Bicycle {self.id}"

@dataclass(frozen=True)
class Glider:
    size: int

    def display(self) -> str:
        return f"Glider {self.size}"

def show(t: Displayable) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
#: Bicycle Bob
#: Glider 65
```

A structural type describes the required shape,
and the checker verifies it ahead of time.
Dynamic typing and protocols are the same idea, checked at different times.

The `ABC` in `shapes_oo.py` and this `Protocol` are lookalikes that differ in who must know about whom.
An abstract base class is *nominal*: a type joins by inheriting from it,
the membership is declared in the subclass's own source,
and the base can carry shared implementation for its children.
A protocol is *structural*:
any type with the right members already satisfies it,
including types in libraries you cannot edit,
and the type's author never needs to hear that your protocol exists.
That independence is why this chapter leans on protocols.
They connect pieces without requiring any piece to change.

A protocol also sharpens what [the Liskov Substitution Principle](#liskov-substitution)
does and does not get you.
Satisfying `Displayable` is a shape claim: the method exists,
with the right signature, and the checker verifies that half of the contract.
The other half is semantic.
`display()` must also behave the way callers rely on:
return a description rather than raise, finish rather than block,
describe the object rather than change it.
No checker sees that half.
Substitution is safe only when both halves hold,
whether membership came from inheriting a base class or matching a protocol.
The machine checks the signatures; you still owe the behavior.

A third answer names a closed set of types as a union and dispatches with `match`,
introduced in [Pattern Matching](13_Pattern_Matching.md#exhaustive-matching).
The shapes become immutable data, and one free function handles each case.
No base class or overridden method exists.
The type checker confirms the match covers every shape:

```python
# shapes_match.py
import math
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class Rectangle:
    length: float
    width: float

@dataclass(frozen=True)
class Circle:
    radius: float

type Shape = Rectangle | Circle

def area(shape: Shape) -> float:
    match shape:
        case Rectangle(length=length, width=width):
            return length * width
        case Circle(radius=radius):
            return math.pi * radius**2
        case _:
            assert_never(shape)

if __name__ == "__main__":
    shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0)]
    for shape in shapes:
        print(round(area(shape), 4))
#: 3.1416
#: 12.0
```

Choose the approach depending on how the code will grow.
Adding a new shape is easier in the object version because you write one class.
Adding a new operation over all shapes is easier in the data version.
You write one function, and the type checker tells you if you missed a case.
The OOP approach assumes you add types more often than operations,
which is often not true.
[Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
and [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch)
explore this trade-off.

Testing confirms the object-oriented and `match` versions compute the same areas:

```python
# test_shapes.py
import shapes_match as sm
import shapes_oo as so

def test_oo_and_match_shapes_agree() -> None:
    assert (so.Rectangle(3.0, 4.0).area()
            == sm.area(sm.Rectangle(3.0, 4.0)))
    assert so.Circle(1.0).area() == sm.area(sm.Circle(1.0))
```

## Null Object

Polymorphism also removes the most common conditional, the `None` check.
A parameter typed `T | None` makes every use a branch.
Here a logger is optional, so the function guards each logging call:

```python
# optional_logger.py

class ListLogger:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def log(self, message: str) -> None:
        self.lines.append(message)

def total(prices: list[float],
          logger: ListLogger | None = None) -> float:
    result = 0.0
    for price in prices:
        result += price
        if logger is not None:
            logger.log(f"added {price}, total {result}")
    return result

if __name__ == "__main__":
    print(total([1.5, 2.5]))
    logger = ListLogger()
    print(total([1.5, 2.5], logger), len(logger.lines))
#: 4.0
#: 4.0 2
```

The checker insists on the guard, and it is right to insist.
Without it, a `None` eventually meets `.log()` and the call fails.
But look at what the `None` branch does: nothing.
Doing nothing is behavior, and behavior belongs in an object.

The *Null Object* pattern replaces "absent" with an object whose behavior is neutral.
Give the do-nothing case a class,
and the optional parameter becomes an ordinary required one with a default:

```python
# null_logger.py
from typing import Final, Protocol

class Logs(Protocol):
    def log(self, message: str) -> None: ...

class NullLogger:
    def log(self, message: str) -> None:
        pass

SILENT: Final[NullLogger] = NullLogger()

class ListLogger:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def log(self, message: str) -> None:
        self.lines.append(message)

def total(prices: list[float],
          logger: Logs = SILENT) -> float:
    result = 0.0
    for price in prices:
        result += price
        logger.log(f"added {price}, total {result}")
    return result

if __name__ == "__main__":
    print(total([1.5, 2.5]))
    logger = ListLogger()
    print(total([1.5, 2.5], logger), len(logger.lines))
#: 4.0
#: 4.0 2
```

The output is identical and the branches are gone.
`total()` decides nothing about logging.
`NullLogger` defines silence once, instead of every call site defining it.
The parameter's type improved too.
`Logs` is a protocol, so any logger fits, and no caller ever sees a `| None`.
Because `NullLogger` is stateless,
one shared `SILENT` instance serves the whole program,
and it is safe as a default argument value.
The standard library ships this exact object as `logging.NullHandler`,
and the maze in [Simulation](38_Simulation.md)
points every doorless direction at one shared `EDGE` room,
so movement code never checks for `None`.

```python
# test_null_logger.py
import null_logger as nl
import optional_logger as ol

def test_versions_agree() -> None:
    prices = [1.0, 2.0, 3.5]
    assert ol.total(prices) == nl.total(prices) == 6.5

def test_list_logger_records_each_step() -> None:
    logger = nl.ListLogger()
    nl.total([1.0, 2.0], logger)
    assert logger.lines == [
        "added 1.0, total 1.0", "added 2.0, total 3.0"]
```

Null objects stand in for "nothing to do," not "nothing there."
When a caller must notice absence,
a lookup that can fail or a required value that may be missing,
a silent stand-in buries the problem.
Keep `T | None` there,
or return the `Result` of [Error Handling](42_Functional_Error_Handling.md#a-result-type),
so the type forces callers to face the missing case.
The test is what callers would write.
If every one of them would handle absence with the same neutral behavior,
centralize that behavior in a null object.
If any caller would branch differently, absence is information,
and it belongs in the type.

## OOP Is Still Sometimes Useful

None of this means objects are a mistake.
They improved real things.
A class is a clean namespace with dot-completion.
A class guarantees initialization and, as a data class, generates equality,
representation, and, when frozen, hashing.

OOP also normalized the crucial idea of types,
as seen in [Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values).
If you simply avoid implementation inheritance,
the payoff for using types is tremendous.

Start with functions and data.
When a program truly needs an object, it tells you.
You find yourself passing the same data into every function,
or you need to bundle behavior with state.
Objects are useful sometimes.
They do not need to be everywhere, all the time.

## Guidelines

- Prefer immutable data structures over encapsulation.
- Prefer functions over methods.
- Prefer composing structures over inheriting implementation.
- Use protocols to fit pieces together, rather than a base-class hierarchy.
- Prioritize simplicity, clarity, and maintainability.
  Those produce reliability.

The rest of this book is about design patterns.
Many of them arose to work around limitations of older object-oriented languages.
Read them through the lens of this chapter.
For each pattern, ask whether you need the objects and the inheritance,
or whether immutable data, a function, and a protocol already solve the problem.

## Exercises

1.  In `leaky.py`, add a `tags: list[str]` field to `Leaky`,
    exposed through a `@property` the same way `numbers` is,
    and demonstrate the same leak by mutating the list you get back.
    Then plug the leak the way `plugged.py` plugs `numbers` and `bob`.
2.  In `immutable.py`, change `numbers: tuple[int, ...]` to `list[int]` and rerun `ty check`.
    Notice that it does not object:
    the checker sees nothing wrong with a mutable field in a frozen class.
    Demonstrate the leak with an `append()`, then restore the `tuple`.
    Who, then, is responsible for making immutability go all the way down?
3.  In `point_distance.py`,
    add a third point `p3 = Point(6, 8)` and confirm `distance(p1, p3)` and `p1.distance_to(p3)` still agree.
4.  In `distance_protocol.py`, add a third class, `Triple`, with fields `a`,
    `b`, `c` (no `x` or `y`),
    and an adapter `TripleCoord` that exposes `x` as `a` and `y` as `b`,
    ignoring `c`.
    Confirm `distance()` works on a `TripleCoord` with no change to `distance()` itself.
5.  In `shapes_match.py`, add a new shape, `Square(side: float)`,
    to the `Shape` union, add its `case` to `area()`,
    and confirm `ty check` still passes.
    Then temporarily comment out the new `case` and observe what `assert_never()` causes the checker to report.
6.  In `null_logger.py`, write a second null-object style class, `NullCache`,
    whose `get(key)` always returns `None` and whose `set(key, value)` does nothing,
    following the same shape as `NullLogger`.
