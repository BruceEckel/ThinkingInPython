# Rethinking Objects

I spent much of my career promoting objects.
I wrote *Thinking in C++* and *Thinking in Java*,
served on the C++ Standards Committee for its first eight years,
and toured the world giving object-oriented programming (OOP) presentations.
When I say I have come to doubt that objects should be the default,
it is not an outsider's complaint.

This part of the book is about design patterns,
most of which assume objects and inheritance.
First, however, I want to question how much of that machinery you need.
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
Not everything in Simula was an object.
The language still had standalone functions.
It was a compiled, statically typed language,
so the discipline later named the Liskov Substitution Principle (LSP)
fit naturally.

*Smalltalk* took the other path: everything is an object,
and you act on them only by sending messages, always late-bound.
It was an emphatically dynamic,
runtime world where you built programs by finding the closest existing object and inheriting from it to add behavior.
That style guarantees nothing about substitutability.

*C++* drew from Simula.
Objects were optional,
and it brought object-oriented programming and exceptions into the mainstream.

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
They compose data structures instead of inheriting implementation.
They let code live outside classes,
so one function can serve many types instead of becoming a method on each.
The industry has been quietly walking back from "everything is an object" and from implementation inheritance.

## The Liskov Substitution Principle {#liskov-substitution}

The *Liskov Substitution Principle* (LSP)
says that an object of a subtype must work anywhere code expects an object of its base type.
A subclass may add behavior, but it must honor the base class contract.
An override may accept more than the base does but never less.
It returns a result the caller can use where it expects the base's result,
and raises no surprising exceptions.
When subclasses obey it,
code you write against the base class works unchanged on any of them.
This makes polymorphism,
and patterns like the [Template Method](25_Patterns--Template_Method.md), safe.
A statically typed compiler can check that an override's signature stays compatible.
It cannot check whether the override behaves the way the base class declares.
The base class calls a method and trusts every subclass to stand in for it.

Python has no such compiler,
but the line between what a tool checks and what it cannot falls in the same place.
A type checker reads an override's signature and reports one that no longer fits,
especially when [`@override`](07_Foundations--Classes.md#marking-overrides-with-override)
marks the intent.
No tool reads the behavior behind the signature.
Nothing stops a subclass from breaking the base class contract while matching its signature perfectly.
The interpreter runs code that violates the LSP without objection.
That code may or may not fail at runtime:

```python
# lsp_violation.py
from dataclasses import dataclass, field
from typing import ClassVar, override

@dataclass
class Stack:
    items: list[int] = field(default_factory=list)

    def push(self, item: int) -> None:
        self.items.append(item)

@dataclass
class BoundedStack(Stack):
    limit: ClassVar[int] = 2

    @override
    def push(self, item: int) -> None:
        if len(self.items) >= self.limit:
            raise OverflowError("Stack is full")
        super().push(item)

def fill(stack: Stack, count: int) -> int:
    for n in range(count):
        stack.push(n)
    return len(stack.items)

print(fill(Stack(), 5))
#: 5
try:
    fill(BoundedStack(), 5)
except OverflowError as e:
    print(e)
#: Stack is full
```

`BoundedStack.push()` takes the same argument and returns the same type,
so `@override` holds and `ty` reports nothing.
`fill()` targets `Stack`, which never refuses a `push()`,
and a `BoundedStack` handed to it raises an exception on the third item.
The subclass matches the signature and breaks the contract behind it.

Substitutability is the first thing OOP promised that no tool can check.
OOP made four promises: encapsulation,
behavior bundled into the object as methods, reuse through inheritance,
and polymorphism.
The next sections take them one at a time,
and ask of each what Python delivers and what it costs.

## Encapsulation Leaks

The first OOP promise is encapsulation: hide the data,
expose it only through methods you control.
Python hides a field with a leading underscore and a read-only property.
This does not work as well as it looks.
A getter that returns a mutable object hands the caller a reference to the underlying internals:

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
    # The same object
    print(leaky.numbers is leaky._numbers)
    # Both mutate "private" internals through the getters:
    leaky.numbers.append(999)
    leaky.bob.name = "Ralph"
    print(leaky.numbers, leaky.bob)
#: True
#: [1, 2, 999] Bob(name='Ralph')
```

Encapsulation with private fields and getters still leaks.
The `is` check shows the mechanism:
the getter returns no view or snapshot of the list, but a reference to the list,
the identical object the underscore hides.
Python's `return` hands out references, never copies.
The property blocks reassigning `numbers`,
but cannot stop the caller from mutating the list it returns.

## Plugging Leaks Is Tedious

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
        # Isolate by returning a copy
        return self._numbers.copy()

    @property
    def bob(self) -> Bob:
        return deepcopy(self._bob)

if __name__ == "__main__":
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates the copy
    plugged.bob.name = "Ralph"  # Ditto
    print(plugged.numbers, plugged.bob)
#: [1, 2] Bob(name='Bob')
```

Now the internals are safe, but at a cost: private fields, getters,
and defensive copies, all to stop other code from changing your data.
And these copies plug only the outbound leak.
The constructor stores the caller's own list,
so the caller's original reference still mutates the internals.
A fully defensive class must copy on the way in as well.

A `@dataclass` version of `Plugged` trims the constructor,
but its generated `__repr__` prints `_numbers` and `_bob` directly,
leaking the internals yet again.

The two getters also copy differently, and the difference is its own trap.
`list.copy()` is *shallow*: it duplicates the container but shares the elements,
which is safe here only because the elements are immutable `int`s.
`Bob` gets `deepcopy()`,
which recursively copies everything the object references,
the conservative choice when a field's own fields might be mutable.
A shallow copy of a list of `Bob`s plugs nothing:
the caller's copy of the list still holds your actual `Bob`s.

The test confirms the defensive copy holds.
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
If the data cannot change, you have nothing to protect.
If you freeze it, the whole apparatus disappears.
The fields are public, with no getters and no copies:

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
    # and .bob.name = "Ralph" raises FrozenInstanceError.
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

The test goes through `setattr()` because the type checker rejects `immutable.bob.name = "Ralph"`.
`frozen=True` is the defense that holds at runtime,
against code the type checker never saw.

Two quiet changes in the listing do as much work as `frozen=True`:
`numbers` is a `tuple`, not a `list`, and `Bob` carries `frozen=True` too.
`frozen=True` is shallow:
it stops assignment to the fields of `Immutable` itself,
but it cannot stop mutation inside a field that is itself mutable.
If you declare the field as a `list` instead, the leak reopens:

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
    print(e)
#: cannot assign to field 'numbers'
try:
    # A list field makes the whole instance unhashable
    hash(fl)
except TypeError as e:
    print(e)
#: unhashable type: 'list'
```

Frozen guards the binding, not the object.
`fl.numbers` must keep pointing at the same list,
and attempting to rebind it raises an exception.
But nothing stops that list from changing, the identical leak `Leaky` has.
Hashing goes the same way.
A frozen data class is hashable only when every field it holds is hashable,
so `hash(fl)` raises a `TypeError` and a `FrozenLeaky` cannot be a dict key.
The listing shows all three side by side: the rebinding `frozen=True` catches,
and the mutation and the failed hash it does not.
That is why `immutable.py` needs those two changes.
Immutability pays off only when it goes all the way down.

[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#immutability)
makes the fuller case for frozen data classes.

## Methods or Functions?

The second OOP promise is behavior inside the object, as methods.
But a method is only a function whose first argument is the object.
Compare a method `distance_to()` to a function `distance()` that does the same thing:

```python
# point_distance.py
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:  # Method
        return sqrt((other.x - self.x) ** 2
                    + (other.y - self.y) ** 2)

def distance(a: Point, b: Point) -> float:  # Free function
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

if __name__ == "__main__":
    # A 3-4-5 right triangle
    p1, p2 = Point(3, 0), Point(0, 4)
    print(p1.distance_to(p2))
    # The method, as a function
    print(Point.distance_to(p1, p2))
    print(distance(p1, p2))
#: 5.0
#: 5.0
#: 5.0
```

The middle call shows the method called as if it were a free function.
When you fetch it from the class instead of from an instance,
`distance_to` is an ordinary function,
and the call passes `p1` as the first argument.
`p1.distance_to(p2)` is shorthand for that call.
The dot fills in `self`.
The function reads the same and computes the same.
It is not worse, and it has an advantage.
It need not live inside `Point`.

## Protocols Generalize, Composition Adapts

When the function does not belong to a class,
it can work on anything shaped like a point.
A `Protocol` describes that shape,
and any type with matching attributes satisfies it, without inheritance.
This is [structural typing](08_Foundations--Static_Types.md#structural-typing-with-protocols).
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
# Adapter: uses composition, not inheritance
class PairCoord:
    pair: Pair

    @property
    def x(self) -> float:
        return self.pair.a

    @property
    def y(self) -> float:
        return self.pair.b

if __name__ == "__main__":
    print(distance(Point(3, 0), Point(0, 4)))
    print(distance(PairCoord(Pair(3, 0)),
                   PairCoord(Pair(0, 4))))
#: 5.0
#: 5.0
```

`Point` and `PairCoord` share no base class.
They both have `x` and `y`, which is all `distance()` requires.
`Coord` declares `x` and `y` as properties rather than as bare `x: float` annotations.
A bare annotation in a protocol is a read-write attribute,
so an implementer must allow assignment to it.
Neither class here allows it: `PairCoord` computes `x` from its `Pair`,
and the frozen `Point` rejects assignment to every field,
so both satisfy the property form and both fail the annotation form.
Declare a protocol member read-only unless callers really do write to it.

## Prefer Composition to Inheritance

The third OOP promise is reuse through inheritance.
In practice, implementation inheritance couples a subclass to its base in ways that are hard to undo:

```python
# counting_list.py
from typing import override

class CountingList(list[int]):
    def __init__(self) -> None:
        super().__init__()
        self.appends = 0

    @override
    def append(self, item: int, /) -> None:
        self.appends += 1
        super().append(item)

counted = CountingList()
counted.append(1)
counted.extend([2, 3])
print(len(counted), counted.appends)
#: 3 1
```

`list.extend()` appends its items without calling `append()`,
so the count is wrong the moment anyone uses the base class's other method.
Nothing in the subclass is incorrect.
It inherits an implementation and now depends on that implementation's details,
which is a fact about `list` that no signature records and no type checker reports.
This is the *fragile base class* problem:
a base class cannot change its own internals without risking every subclass that came to depend on them.

Composition answers it by delegation.
Hold a list instead of being one, and expose only what you meant to expose:

```python
# counting_box.py
from dataclasses import dataclass, field

@dataclass
class CountingBox:
    items: list[int] = field(default_factory=list)
    appends: int = 0

    def append(self, item: int) -> None:
        self.appends += 1
        self.items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

box = CountingBox()
box.append(1)
box.extend([2, 3])
print(len(box.items), box.appends)
#: 3 3
```

Nothing arrives from a base class, so nothing slips past the counter:
the only way into `items` is a method this class wrote.
`CountingBox` forwards every operation by hand.
`CountingList` inherits hundreds it didn't write, and gets one wrong.
Composition does not make the counting bug impossible.
If `extend()` calls `self.items.extend(more)` instead of going through `append()`,
the count is still wrong.
The difference is where the bug lives: in the class you read,
not in `list` internals hidden in `CountingList`.

Composition does more than repair a broken subclass.
A type holds other types as fields,
and frozen instances compare by value and work as keys:

```python
# composition.py
from dataclasses import dataclass

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
    Name("Gerald", "Spigot-Farthingale"),
    Address("Sodding-on-the-Wold", "12345")
)
print(c.name)
#: Name(first='Gerald', last='Spigot-Farthingale')
print(c.address)
#: Address(city='Sodding-on-the-Wold', postal='12345')

twin = Contact(
    Name("Gerald", "Spigot-Farthingale"),
    Address("Sodding-on-the-Wold", "12345")
)
print(c == twin)  # Value equality, field by field
#: True
# Hashable, so it works as a dict key
print({c: "value"}[c])
#: value
```

`Contact` inherits nothing, and gains no methods it did not request.
It holds a `Name` and an `Address`, and those types stay usable on their own.
The arrangement has a cost:
changing one city means rebuilding the `Address` and then the `Contact`.
[The General Form of `replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
makes that rebuild routine.
The last two lines are the payoff.
Two contacts built from equal parts are equal, and the whole structure hashes,
because value equality and hashing follow from the fields rather than from a base class.

## Polymorphism Without Inheritance

The fourth OOP promise is polymorphism.

### What Is Polymorphism?

Polymorphism means that a function parameter accepts more than one type.
Inheritance is only one way to get there.
The questions are which types it accepts and what the function may do with them.

Type theory defines three kinds of polymorphism.
Christopher Strachey's 1967 lecture notes,
[Fundamental Concepts in Programming Languages](http://fpl.cs.depaul.edu/jriely/447/assets/articles/strachey-fundamental-concepts-in-programming-languages.pdf),
named the first two, parametric and ad-hoc.
Cardelli and Wegner added the third, subtyping,
in 1985^[*On Understanding Types, Data Abstraction, and Polymorphism*, where subtyping appears as *inclusion polymorphism*.].

*Subtype polymorphism* is what the four subsections below demonstrate.
One function accepts any type that fits a shape,
whether that shape comes from inheriting an `ABC` or matching a `Protocol`.
You write one function.
The type varies underneath it.

*Parametric polymorphism* is a single implementation for multiple types.
[Static Types](08_Foundations--Static_Types.md#generic-functions-and-classes)'s `first[T]` and `Box[T]` show this.
One body works for any `T`.
The type checker infers the concrete type behind `T` at each call site.

With *ad-hoc polymorphism* (typically *function overloading*),
a different implementation handles each type,
and the argument's type selects which one runs.
Python's version of ad-hoc polymorphism is `@overload`,
which lets one function name have multiple typed signatures over a single implementation that branches at runtime:

```python
# overload_example.py
from typing import overload

@overload
def stringify(value: int) -> str: ...

@overload
def stringify(value: list[int]) -> list[str]: ...

def stringify(value: int | list[int]) -> str | list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return str(value)

if __name__ == "__main__":
    print(stringify(42))
    print(stringify([1, 2, 3]))
#: 42
#: ['1', '2', '3']
```

Each `@overload` line is a declaration for the type checker,
not a function that runs.
Only the last, unmarked definition executes.
`stringify(42)` checks as returning `str`,
and `stringify([1, 2, 3])` checks as returning `list[str]`,
even though both calls run the same branching body.

[`singledispatch`](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
is ad-hoc polymorphism's other Python form.
It uses genuinely separate functions per type,
instead of one function branching internally.

### Abstract Base Classes

The classic object-oriented example uses an abstract base class:

```python
# shapes_oo.py
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

@dataclass(frozen=True)
class Rectangle(Shape):
    length: float
    width: float

    @override
    def area(self) -> float:
        return self.length * self.width

@dataclass(frozen=True)
class Circle(Shape):
    radius: float

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

### Dynamic Typing

With dynamic typing, any type works as long as it has the necessary methods.
No shared base class or declared set of types constrains the parameter,
and the only validity check comes at runtime, when the call runs:

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

`show()` accepts anything because `t`'s type is `Any`,
which is not the same as `object`.
If you pass it something without a `display()` method,
the call raises an exception when the line runs.
If you use `t: object` (the safe top type),
`show()` fails the type checker because `object` has no `display()` method.
`Any` switches the type checker off for `t`, so any type passes.
Each `Any` parameter moves you back into dynamic typing.

### Protocols

[`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
re-establishes static typing:

```python
# protocols_typed.py
from typing import Protocol
from dynamic_typing import Bicycle, Glider

class Displayable(Protocol):
    def display(self) -> str: ...

def show(t: Displayable) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
#: Bicycle Bob
#: Glider 65
```

A structural type describes the required shape,
and the type checker verifies it ahead of time.
Dynamic typing and protocols are the same idea, checked at different times.

An abstract base class is *nominal* (named): a type joins by inheriting from it.
The subclass's own source declares membership,
and the base can carry shared implementation for its children.
A protocol is *structural*: it works with any type that has matching members.
This includes types in libraries you cannot edit.
The type's author need not hear that your protocol exists.
That independence is why this chapter emphasizes protocols.
They connect pieces without requiring any piece to change.

Because membership is structural,
one class can satisfy any number of protocols at once,
with no inheritance graph connecting them.
Each protocol names only the shape it needs.
Nothing forces `Invoice` below to acknowledge `Priced`, `Serializable`,
or `Describable`.

Classic multiple inheritance has the *diamond problem*.
If two base classes trace back to a common ancestor,
the interpreter must pick which version of an overridden method to call.
Protocols avoid that question.
Satisfying three of them costs nothing more than having the three methods:

```python
# multi_protocol.py
import json
from dataclasses import asdict, dataclass
from typing import Protocol

class Priced(Protocol):
    def total(self) -> float: ...

class Serializable(Protocol):
    def to_json(self) -> str: ...

class Describable(Protocol):
    def describe(self) -> str: ...

@dataclass(frozen=True)
class Invoice:
    amount: float
    customer: str

    def total(self) -> float:
        return self.amount

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    def describe(self) -> str:
        return f"Invoice for {self.customer}"

def charge(item: Priced) -> float:
    return item.total()

def persist(item: Serializable) -> str:
    return item.to_json()

def audit(item: Describable) -> str:
    return item.describe()

if __name__ == "__main__":
    invoice = Invoice(19.99, "Ada")
    print(charge(invoice))
    print(persist(invoice))
    print(audit(invoice))
#: 19.99
#: {"amount": 19.99, "customer": "Ada"}
#: Invoice for Ada
```

`Invoice` inherits from `object` alone, yet `charge()`, `persist()`,
and `audit()` each accept it, because each only checks the one method it needs.

#### What the Shape Does Not Say

That same structural check has a blind spot.
Two unrelated protocols can share a method name and signature by coincidence,
and nothing distinguishes them:

```python
# protocol_collision.py
from dataclasses import dataclass
from typing import Protocol

class Priced(Protocol):
    def total(self) -> float: ...

class Weighted(Protocol):
    def total(self) -> float: ...

@dataclass(frozen=True)
class Package:
    weight_kg: float

    def total(self) -> float:
        return self.weight_kg  # Weight, not a price

def charge(item: Priced) -> float:
    return item.total()

if __name__ == "__main__":
    package = Package(4.5)
    print(charge(package))  # Silently treated as a price
#: 4.5
```

`ty` accepts `package` as a `Priced` argument without complaint,
and `charge()` returns `4.5`, silently treating a weight as a price.
The type checker matches the shape correctly.
The mismatch lives in what the number means, and no type checker sees that.

A distinct type per concept could close this gap.
`typing.NewType` looks like the natural fix:

```python
# newtype_boundary.py
from typing import NewType

UserId = NewType("UserId", int)

def lookup(uid: UserId) -> str:
    return f"user-{uid}"

if __name__ == "__main__":
    print(lookup(UserId(42)))
    # ty: expected "UserId", found "Literal[42]":
    print(lookup(42))  # type: ignore
#: user-42
#: user-42
```

Without the `# type: ignore`, `ty` rejects the second call.
`UserId` and `int` are different types to the type checker.
The same distinction would separate `Priced` from `Weighted` in `protocol_collision.py` if `total()` returned a `Price` or a `Weight` instead of a bare `float`.

`NewType` is only an aid during type checking.
It builds no wrapper object.
At runtime it is the identity function, so `UserId(42)` is `42`:

```python
# test_newtype_boundary.py
from newtype_boundary import UserId

def test_newtype_has_no_runtime_effect() -> None:
    assert UserId(42) == 42
    assert type(UserId(42)) is int
```

Nothing in that test can fail.
The `NewType` protection lives in the type checker alone.
Passing a raw `int` where a signature says `UserId` raises no exception.
In `newtype_boundary.py`,
the `# type: ignore` silences that diagnostic so the rejected call can run anyway.
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#composing-types-from-types)
takes the other route.
A frozen dataclass with a validating `__post_init__` enforces the distinction at runtime too,
at the cost of a constructor call instead of a bare literal.

A protocol also sharpens what [the Liskov Substitution Principle](#liskov-substitution)
does and does not get you.
Satisfying a protocol is a shape claim: the methods exist,
with the correct signatures,
and the type checker verifies that half of the contract.
The other half is semantic.
A method must also behave the way callers expect.
For example, return a description rather than raise an exception,
finish rather than block, describe the object rather than change it.
No type checker sees that half.
Substitution is safe only when both halves work,
whether membership comes from inheriting a base class or matching a protocol.

### Pattern Matching on a Union

Another approach uses a union and a `match`,
introduced in [Pattern Matching](13_Techniques--Pattern_Matching.md#exhaustive-matching).
The shapes become immutable data, and one free function handles all the cases,
with no base class and no overridden methods.
The type checker ensures that the match covers every shape.
Here is `shapes_oo.py` modified to use pattern matching:

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

Adding a new shape is easier in the OOP version because you write one class.
Adding a new operation over all shapes is easier in the pattern matching
(functional) version,
where the operation is one new function rather than a new method on every class.
The exhaustiveness check covers the other direction.
Adding a member to the `Shape` union leaves every existing `match` incomplete,
and `assert_never()` turns each one into a type checker error naming the shape you missed.

The OOP approach assumes you add types more often than operations,
which is often not true.
This trade-off is the expression problem from [Pattern Matching](13_Techniques--Pattern_Matching.md#dynamic-binding-vs.-pattern-matching).
[Multiple Dispatching](32_Patterns--Multiple_Dispatching.md#one-type-or-many)
and [Visitor](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
explore it further.

## Null Object

Polymorphism removes the most common conditional, the `None` check.
A parameter typed `T | None` reintroduces that check everywhere the parameter appears.
Here a logger is optional, so the function guards each logging call:

```python
# optional_logger.py
from dataclasses import dataclass, field

@dataclass
class ListLogger:
    lines: list[str] = field(default_factory=list)

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

The type checker correctly insists on the guard.
Without it, a `None` eventually meets `.log()` and the call fails.
The `None` branch does nothing.
Doing nothing is behavior, and behavior belongs in an object.

The *Null Object* pattern replaces "absent" with an object whose behavior is neutral.
If you give the do-nothing case a class,
the optional parameter becomes required, with a default:

```python
# null_logger.py
from typing import Final, Protocol
from optional_logger import ListLogger

class Logs(Protocol):
    def log(self, message: str) -> None: ...

class NullLogger:
    def log(self, message: str) -> None:
        pass

SILENT: Final[NullLogger] = NullLogger()

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

`total()` decides nothing about logging.
`NullLogger` defines silence once, instead of every call site defining it.
The parameter's type also improves.
`Logs` is a protocol, so any logger fits, and no caller sees a `| None`.
Because `NullLogger` is stateless,
one shared `SILENT` instance serves the whole program,
and it is safe as a default argument value.
The standard library includes this idea as `logging.NullHandler`,
and the maze in [Simulation](38_Patterns--Simulation.md)
points every doorless direction at one shared `EDGE` room,
so movement code never checks for `None`.

Null objects stand in for "nothing to do," not `None`'s "nothing there."
Sometimes a caller must notice absence,
like a lookup that can fail or a required value that may be missing.
In these cases, use `T | None`,
or return [`Result`](42_Functional--Error_Handling.md#a-result-type),
so the type forces callers to face the missing case.

If every decision handles absence with the same neutral behavior,
centralize that behavior in a null object.
If any caller branches differently, then absence is information,
and it belongs in the type.

## OOP Is Useful, Sometimes

None of this means objects are a mistake.
A class is a clean namespace with dot-completion.
A class guarantees initialization and, as a data class, generates equality,
representation, and, when frozen, hashing.

OOP also normalized the idea of types,
which [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
takes further.
If you avoid implementation inheritance,
the payoff for using types is tremendous.

Start with functions and data.
When a program truly needs an object, it tells you:
you are passing the same data into every function,
or bundling behavior with state.
OOP is useful, sometimes.
But not everywhere, all the time.

## Guidelines

- Prefer immutable data structures over encapsulation.
- Prefer functions over methods.
- Prefer composing structures over inheriting implementation.
- Prefer protocols over a base-class hierarchy.
- Prioritize simplicity, clarity, and maintainability, to produce reliability.

Many of the design patterns in this part of the book arose to work around limitations of older object-oriented languages.
Read them through the lens of this chapter.
For each pattern, ask whether you need the objects and the inheritance,
or whether immutable data, a function, and a protocol already solve the problem.

## Exercises

1.  In `leaky.py`, add a `tags: list[str]` field to `Leaky`,
    exposed through a `@property` the same way `numbers` is,
    and demonstrate the same leak by mutating the list you get back.
    Then plug the leak the way `plugged.py` plugs `numbers` and `bob`.
2.  In `immutable.py`, change `numbers: tuple[int, ...]` to `list[int]`.
    Show that `ty check` still passes, that `append()` works,
    and that `hash(immutable)` now raises a `TypeError`,
    so the frozen instance can no longer be a dict key.
    Restore the `tuple`.
    Who, then, must make immutability go all the way down?
3.  In `protocol_collision.py`,
    define `Price = NewType("Price", float)` and `Weight = NewType("Weight", float)`,
    change `Priced.total()` to return a `Price`,
    `Weighted.total()` to return a `Weight`,
    and `Package.total()` to return a `Weight`.
    Run `ty check` and read the error it reports for `charge(package)`.
    Then say what still goes wrong at runtime if someone deletes the annotations.
4.  In `distance_protocol.py`, add a third class, `Triple`, with fields `a`,
    `b`, `c` (no `x` or `y`),
    and an adapter `TripleCoord` that exposes `x` as `a` and `y` as `b`,
    ignoring `c`.
    Confirm `distance()` works on a `TripleCoord` with no change to `distance()` itself.
5.  In `shapes_match.py`, add a new shape, `Square(side: float)`,
    to the `Shape` union, add its `case` to `area()`,
    and confirm `ty check` still passes.
    Then temporarily comment out the new `case` and observe what `assert_never()` causes the type checker to report.
6.  In `null_logger.py`, write a second null-object style class, `NullCache`,
    whose `get(key)` always returns `None` and whose `set(key, value)` does nothing,
    following the same shape as `NullLogger`.
7.  In `counting_list.py`, count `__setitem__` as well,
    then find a second `list` method that changes the contents without going through either override.
    Rewrite `CountingList` to hold a list instead of inheriting from one,
    and show that the counts are now correct for every route in.
8.  In `lsp_violation.py`,
    make `BoundedStack` obey the Liskov Substitution Principle without removing the limit:
    keep the base contract that `push()` always succeeds,
    and expose "full" some other way.
    Then say what you gave up,
    and whether `BoundedStack` should have been a subclass of `Stack` at all.
