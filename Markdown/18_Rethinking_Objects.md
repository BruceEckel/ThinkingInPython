# Rethinking Objects

I spent much of my career promoting objects.
I wrote *Thinking in C++* and *Thinking in Java*,
served on the C++ Standards Committee for its first eight years,
and toured the world giving object-oriented programming talks.
So when I say I have come to doubt that objects should be the default,
it is not an outsider's complaint.

We are about to spend the rest of this book on design patterns,
and most of them assume objects and inheritance.
Before we start, I want to question how much of that machinery we actually need.
This chapter is adapted from my PyCon 2023 talk,
[Rethinking Objects](https://github.com/BruceEckel/RethinkingObjects).

## It Is Evolution

Languages evolve to fit their environment.
A feature that looks strange now usually made sense for the problem,
and the hardware, of its time.
It helps to look at where objects came from.

*Simula* introduced objects in the 1960s to model simulations:
a system is a set of things that interact.
Notably, not everything was an object.
Simula still had standalone functions.
It was a compiled, statically typed language,
so the idea that a subtype should be substitutable for its base type,
the Liskov substitution principle, fit naturally.

*Smalltalk* took the other road: everything is an object,
and the only thing you do is send messages to objects, always late-bound.
It was a gloriously dynamic,
run-time world where you built programs by finding the closest existing object and inheriting from it to add behavior.
That is the opposite of Liskov substitution.

*C++* drew from Simula.
Objects were optional, and it brought object-oriented programming,
and exceptions, into the mainstream.
*Java* drew from Smalltalk: everything is an object,
even when all you need is a function.
Java is statically compiled, so substitutability matters,
yet it encouraged reusing code by inheriting implementation,
which pulls in the other direction.

Then the newer languages backed away.
Rust, Swift, Go, and Kotlin lean on data structures rather than objects.
They make data immutable by default,
they compose data structures instead of inheriting implementation,
and they let code live outside classes, which cuts duplication.
The industry has been quietly walking away from "everything is an object" and from implementation inheritance.
The rest of this chapter shows why, in Python.

## Encapsulation Leaks

The first promise of objects is encapsulation: hide the data,
expose it only through methods you control.
In Python the usual move is a leading underscore and a read-only property.
It does not work as well as it looks.
A getter that returns a mutable object hands the caller a reference to the real internals:

```python
# leaky.py
# Encapsulation with private fields and getters still leaks. A
# getter that returns a mutable object hands the caller a reference
# to the real internals.
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
    # Both mutate the "private" internals through the getters:
    leaky.numbers.append(999)
    leaky.bob.name = "Ralph"
    print(leaky.numbers, leaky.bob)
#: [1, 2, 999] Bob(name='Ralph')
```

The output shows that the internals changed from outside.
The property blocked reassigning `numbers`,
but it could not stop the caller from mutating the list it returned.

## Plugging the Leaks Is Tedious

You can stop the leak by copying everything a getter returns.
It works, but every getter has to remember to do it,
and so does every getter in every subclass, forever:

```python
# plugged.py
# Plugging the leaks means defensively copying everything a getter
# returns. It works, but every getter has to remember to do it,
# forever.
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
    plugged.bob.name = "Ralph"   # Ditto
    print(plugged.numbers, plugged.bob)
#: [1, 2] Bob(name='Bob')
```

Now the internals are safe, but look at what we are doing.
We add private fields, getters, and defensive copies,
all to stop other code from changing our data.

## Immutability Dissolves It

Encapsulation is only needed because of mutability.
If the data cannot change, there is nothing to protect.
Freeze it, and the whole apparatus disappears.
The fields are public, there are no getters, and there are no copies:

```python
# immutable.py
# Encapsulation is only needed because of mutability. Freeze the
# data and the problem dissolves: the fields are public, there are
# no getters and no copies, and nothing can leak because nothing can
# change.
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

[Data Classes as Types](10_Data_Classes_as_Types.md#freezing) makes the fuller case for frozen data classes.
Here the point is narrower:
most encapsulation is work you only do because you allowed mutation in the first place.

## Methods or Functions?

The second promise is that behavior belongs inside the object, as methods.
But a method is just a function whose first argument is the object.
Compare a method with a plain function that does the same thing:

```python
# point_distance.py
# A method bound to the class, versus a plain function. The function
# reads the same and computes the same. The class does not need to
# own it.

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
    print(distance(p1, p2))
#: 5.0
#: 5.0
```

The function is not worse.
And it has an advantage: it does not have to live inside `Point`.

## Protocols Generalize, Composition Adapts

Because the function is free, it can work on anything shaped like a point.
A `Protocol` describes that shape,
and any type with the right attributes satisfies it,
with no declared inheritance.
This is the structural typing from [Static Typing](07_Static_Typing.md#structural-typing-with-protocols).
When you are handed a type that does not fit, you adapt it by composition,
not inheritance:

```python
# distance_protocol.py
# The free function generalizes to anything with x and y, described
# by a Protocol. That is the structural typing from the Static Type
# Checking chapter. A class that lacks x and y can be adapted by
# composition, with no inheritance.

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
They both have `x` and `y`, which is all `distance()` asked for.

## Compose, Do Not Inherit

The third promise is reuse through inheritance.
In practice, inheriting implementation couples a subclass to its base in ways that are hard to undo.
The alternative is composition: a type holds other types as fields.
`dataclasses.replace()` gives you the copy-with-changes that immutability needs,
and frozen instances compare by value and can be used as keys:

```python
# composition.py
# Build new types by composing data, not by inheriting
# implementation. replace() copies with changes, and frozen
# instances compare and hash.
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

The fourth promise is polymorphism.
It is usually taught through inheritance, but that is only one form of it.
More broadly, polymorphism means a function parameter accepts more than one type.
The questions are which types it accepts,
and what the function may do with them.
This section draws on my StrangeLoop presentation [Polymorphism Unbound](https://github.com/BruceEckel/PatternMatching).

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
    shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0)]
    for shape in shapes:
        print(round(shape.area(), 4))
```

Inheriting from `ABC` makes `Shape` abstract: it cannot be instantiated, and `@abstractmethod` forces every subclass to define `area()`.

Dynamic typing gives a different answer:
any type works as long as it has the method the function calls.
There is no shared base class and no declared set of types,
and validity is checked only at run time, when the call happens:

```python
# dynamic_typing.py
# Dynamic typing: any type works as long as it has the method that
# gets called. There is no base class and no type union. The check
# happens only at run time, when the method is called.
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
[Static Typing](07_Static_Typing.md#structural-typing-with-protocols) gives this a static form with `Protocol`:
a structural type describes the required shape,
and the checker verifies it ahead of time.
Dynamic typing and protocols are the same idea, checked at different times.

A third answer names a closed set of types as a union and dispatches with `match`,
introduced in [Pattern Matching](11_Pattern_Matching.md#exhaustive-matching).
The shapes become immutable data, and one free function handles each case.
There is no base class and no overridden method,
and the type checker confirms the match covers every shape:

```python
# shapes_match.py
# The same shapes as immutable data, with one free function that
# dispatches by pattern matching. No base class and no overridden
# methods.
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

Which approach is better depends on how the code will grow.
Adding a new *shape* is easier in the object version: write one class.
Adding a new *operation* over all shapes is easier in the data version:
write one function, and the type checker tells you if you missed a case.
The object-oriented default quietly assumes you will add types more often than operations,
which is not always true.
[Multiple Dispatching](30_Multiple_Dispatching.md#one-type-or-many) and [Visitor](31_Visitor.md#the-pythonic-visitor-singledispatch) return to this trade-off.

## Verifying the Claims

Because these are claims about behavior, they belong in tests.
Failures are values here too: a frozen object raises an exception when you try to mutate it.

```python
# test_encapsulation.py
import dataclasses
import pytest
from immutable import Bob, Immutable
from leaky import Leaky
from plugged import Plugged

def test_getter_leaks_internal_state() -> None:
    leaky = Leaky([1, 2])
    leaky.numbers.append(999)  # Reaches the real internal list
    assert leaky.numbers == [1, 2, 999]

def test_defensive_copy_prevents_the_leak() -> None:
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates only a copy
    assert plugged.numbers == [1, 2]

def test_frozen_cannot_be_mutated() -> None:
    immutable = Immutable((1, 2), Bob())
    with pytest.raises(dataclasses.FrozenInstanceError):
        # Frozen, so the assignment fails:
        setattr(immutable.bob, "name", "Ralph")
```

```python
# test_rethinking.py
import distance_protocol as dp
import shapes_match as sm
import shapes_oo as so
from point_distance import Point, distance

def test_method_and_function_agree() -> None:
    p1, p2 = Point(3, 0), Point(0, 4)
    assert p1.distance_to(p2) == 5
    assert distance(p1, p2) == 5

def test_protocol_and_adapter() -> None:
    assert dp.distance(dp.Point(3, 0), dp.Point(0, 4)) == 5
    assert dp.distance(dp.PairCoord(dp.Pair(3, 0)),
                       dp.PairCoord(dp.Pair(0, 4))) == 5

def test_oo_and_match_shapes_agree() -> None:
    assert (so.Rectangle(3.0, 4.0).area()
            == sm.area(sm.Rectangle(3.0, 4.0)))
    assert so.Circle(1.0).area() == sm.area(sm.Circle(1.0))
```

## OOP is Still Sometimes Useful

None of this means objects are a mistake.
They improved real things.
A class is a clean namespace with dot-completion.
A class guarantees initialization and, as a data class, generates equality,
representation, and hashing for free.
Defining a type is itself valuable,
as [Data Classes as Types](10_Data_Classes_as_Types.md#a-type-is-a-set-of-values) argues.

The shift is in the default.
Start with functions and data.
When a program truly wants an object, it tells you:
you find yourself passing the same data into every function,
or you need to bundle behavior with state.
Objects are useful sometimes.
They do not need to be everywhere, all the time.

## Guidelines

Carry these into the chapters that follow:

- Prefer immutable data structures over encapsulation.
- Prefer functions over methods.
- Prefer composing structures over inheriting implementation.
- Use protocols to fit pieces together, rather than a base-class hierarchy.
- Prioritize simplicity, clarity, and maintainability.
  Those produce reliability.

The rest of this book is about design patterns.
Many of them were invented to work around limitations of older object-oriented languages.
Read them through the lens of this chapter.
For each pattern, ask whether you need the objects and the inheritance,
or whether immutable data, a function, and a protocol already solve the problem.
