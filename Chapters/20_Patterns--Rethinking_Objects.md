# Rethinking Objects

> A class bundles data with the code that changes it,
> and inheritance ties classes to each other.
> This chapter separates the parts of that machinery that solve problems from the parts that create them.

I spent much of my career promoting objects.
I wrote *Thinking in C++* and *Thinking in Java*,
served on the C++ Standards Committee for its first eight years,
and toured the world giving object-oriented programming (OOP) presentations.
When I say I have come to doubt that objects should be the default,
I say it as an insider.

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

*Simula* introduced objects in the 1960s to model simulations.
In a simulation, a system is a set of things that interact.
Simula kept standalone functions alongside its objects.
It was a compiled, statically typed language,
so the discipline later named the Liskov Substitution Principle (LSP)
fit naturally.

*Smalltalk* took the other path.
Everything is an object, and you act on objects only by sending messages,
always late-bound.
Smalltalk was emphatically dynamic.
You built a program at runtime by finding the closest existing class and inheriting from it to add behavior.
That style leaves substitutability up to each subclass's author.

*C++* drew from Simula.
Objects were optional.
C++ brought object-oriented programming and exceptions into the mainstream.

*Java* drew from Smalltalk.
Everything lives inside a class,
including code that works as a standalone function.
Java is statically compiled, so substitutability matters.
Yet Java encouraged reusing code by inheriting implementation.
A subclass that inherits code to reuse it need not honor the base's contract.

Newer languages backed away from inheritance.
Rust, Swift, Go, and Kotlin build programs from data structures rather than deep class hierarchies,
and they compose those data structures instead of inheriting implementation.
They let code live outside classes,
so one function can serve many types instead of becoming a method on each.
They favor immutability as well.
Rust makes bindings immutable by default.
Swift and Kotlin encourage immutability through `let` and `val`
(Go has no general immutability).
The industry has been quietly walking back from "everything is an object" and from implementation inheritance.

## The Liskov Substitution Principle {#liskov-substitution}

The *Liskov Substitution Principle* (LSP)
says that an object of a subtype must work anywhere code expects an object of its base type.
A subclass may add behavior, but it must honor the base class contract.
An override may accept more than the base does but never less.
The override returns a result that works wherever the caller expects the base's result,
and its exceptions are ones the caller expects from the base.
When subclasses obey the principle,
code you write against the base class works unchanged on any of them.
That obedience makes polymorphism safe,
and with it patterns like the [*Template Method*](24_Patterns--Template_Method.md).

Code written against the base class calls a method and depends on every subclass standing in for the base.
A statically typed compiler can ensure that an override's signature stays compatible.
It cannot ensure that the override behaves the way the base class declares.

In Python a separate type checker does that compiler's job,
and it stops at the same place that compiler does.
A type checker reads an override's signature and reports one that no longer fits,
especially when [`@override`](07_Foundations--Classes.md#marking-overrides-with-override)
marks the intent.
No tool reads the behavior behind the signature,
so a subclass can break the base class contract while matching that signature perfectly.
The interpreter runs such code unchecked,
and the code may or may not fail at runtime:

```python
# lsp_violation.py
from dataclasses import dataclass, field
from typing import ClassVar, override
from exceptions import expect

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
            raise OverflowError(
                f"Stack is full at {self.limit}")
        super().push(item)

def fill(stack: Stack, count: int) -> int:
    for n in range(count):
        stack.push(n)
    return len(stack.items)

print(fill(Stack(), 5))
#: 5
expect(OverflowError, fill, BoundedStack(), 5)
#: [OverflowError] Stack is full at 2
```

`BoundedStack.push()` takes the same argument and returns the same type as `Stack.push()`,
so the signatures match.
`@override` finds a `push()` in `Stack` to override.
The type checker accepts `BoundedStack` as a `Stack`.
`fill()` takes a `Stack` and relies on its `push()` always succeeding.
The subclass matches the signature and breaks the contract behind it.

No tool catches the broken contract, but a test can.
If a test written against `Stack`'s contract also runs against `BoundedStack`,
the test catches `fill()` failing on the third item.
Two later tests use the same pattern to check other runtime guarantees:
`test_plugged.py` confirms that a getter's copy holds,
and `test_immutable.py` confirms that a frozen field refuses assignment.

Substitutability is the part of polymorphism that no tool can ensure.
OOP made four promises: encapsulation,
behavior bundled into the object as methods, reuse through inheritance,
and polymorphism.
For each one, the question is what Python delivers and where it falls short.

## Encapsulation Leaks

The first OOP promise is encapsulation: hide the data,
expose it only through methods you control.
Python hides a field with a leading underscore and a read-only property.
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

leaky = Leaky([1, 2])
# The same object
print(leaky.numbers is leaky._numbers)
#: True
# Both mutate "private" internals through the getters:
leaky.numbers.append(999)
leaky.bob.name = "Ralph"
print(leaky.numbers, leaky.bob)
#: [1, 2, 999] Bob(name='Ralph')
```

Encapsulation with private fields and getters still leaks.
The `is` check shows the mechanism.
The getter returns a reference to the same list the underscore hides,
not a view or a snapshot of it.
Python's `return` hands out references, not copies.
The property blocks reassigning `numbers`,
but the caller can mutate the list the property returns.

## Plugging Leaks Is Tedious

Copying everything a getter returns stops the leak,
but every getter must make a copy, and so must every getter in every subclass,
forever:

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

Now the internals are safe, but the class needs private fields, getters,
and defensive copies, all to stop other code from changing your data.

These copies plug the outbound leak but leave the inbound one open.
The constructor stores the caller's own list,
so the caller can mutate the internals through that reference.
A fully defensive class must copy on the way in as well as on the way out.

A `@dataclass` version of `Plugged` trims the constructor,
but its generated `__repr__()` prints `_numbers` and `_bob`,
leaking the internals yet again.

The `numbers` and `bob` getters also copy differently.
The wrong kind of copy reopens the leak.
`list.copy()` is shallow,
as [Variables and References](02_Foundations--Tour.md#variables-and-references)
shows for `a[:]`: it duplicates the container but shares the elements.
That sharing is safe here because the elements are immutable `int`s.
`Bob` gets `deepcopy()`,
which recursively copies everything the object references.
A deep copy is the conservative choice when a field's own fields might be mutable.
A shallow copy of a list of `Bob`s protects the list and leaves the `Bob`s shared.
The caller's copy holds the same `Bob` objects as your list,
so the caller can change each one.

A test confirms that the defensive copy holds:

```python
# test_plugged.py
from plugged import Plugged

def test_defensive_copy_prevents_the_leak() -> None:
    plugged = Plugged([1, 2])
    assert plugged.numbers is not plugged._numbers
    plugged.numbers.append(999)
    assert plugged.numbers == [1, 2]
```

## The Immutability Solution

Encapsulation exists mainly because of mutability.
If the data cannot change, you have nothing to protect.
If you freeze it, the private fields, the getters, and the copies all go away.
The fields are public:

```python
# immutable.py
from dataclasses import FrozenInstanceError, dataclass
from exceptions import expect

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
    expect(FrozenInstanceError, setattr,
           immutable.bob, "name", "Ralph")
#: Immutable(numbers=(1, 2), bob=Bob(name='Bob'))
#: [FrozenInstanceError] cannot assign to field 'name'
```

The demo goes through `setattr()` because the type checker rejects `immutable.bob.name = "Ralph"`.
`frozen=True` enforces the rule at runtime,
including in code that skips the type checker.
A test confirms the same guarantee:

```python
# test_immutable.py
import dataclasses
import pytest
from immutable import Bob, Immutable

def test_frozen_field_refuses_assignment() -> None:
    immutable = Immutable((1, 2), Bob())
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(immutable.bob, "name", "Ralph")
```

Two smaller choices in `immutable.py` matter as much as `frozen=True`:
`numbers` is a `tuple`, not a `list`, and `Bob` carries `frozen=True` too.
`frozen=True` is shallow in the same way as the tuple in [Shallow Immutability](03_Foundations--Containers.md#shallow-immutability).
It blocks assignment to the fields of `Immutable`.
A field whose value is mutable stays mutable.
If you declare the field as a `list` instead, the leak reopens:

```python
# frozen_leaky.py
from dataclasses import FrozenInstanceError, dataclass
from exceptions import expect, expected

@dataclass(frozen=True)
class FrozenLeaky:
    numbers: list[int]  # A mutable field in a frozen class

fl = FrozenLeaky([1, 2])
fl.numbers.append(999)  # frozen=True does not stop this
print(fl.numbers)
#: [1, 2, 999]
with expected(FrozenInstanceError):
    fl.numbers = []  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'numbers'
# A list field makes the whole instance unhashable
expect(TypeError, hash, fl)
#: [TypeError] unhashable type: 'list'
```

Frozen guards the binding, not the object.
`fl.numbers` must keep pointing at the same list,
and rebinding it raises a `FrozenInstanceError`.
But the list stays mutable, so `FrozenLeaky` leaks the same way `Leaky` does.

A frozen data class is hashable only when every field it compares is hashable,
so `hash(fl)` raises a `TypeError` and a `FrozenLeaky` cannot be a dict key.
That is why `immutable.py` needs both the `tuple` and the frozen `Bob`.
Immutability lets you share an object safely and use it as a dict key,
but only when the immutability goes all the way down.

Freezing answers the mutation reason for encapsulation.
A second reason survives freezing: representation hiding,
which lets the internal type change later while callers keep working.
A public frozen field gives up that protection.
If you later swap `numbers` from a `tuple` to some other sequence,
every caller that relies on `numbers` being a `tuple` breaks.

[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#immutability)
makes the fuller case for frozen data classes.
The rest of this chapter's listings declare their frozen classes with [`@record`](18_Techniques--Performance.md#record),
which applies `@dataclass(frozen=True, slots=True)` under one name.

## Methods or Functions?

The second OOP promise is behavior inside the object, as methods.
But a method is only a function whose first argument is the object.
Compare a method `distance_to()` to a function `distance()` that does the same thing:

```python
# point_distance.py
from math import sqrt
from record import record

@record
class Point:
    x: float
    y: float

    def distance_to(self, other: Point) -> float:
        return sqrt((other.x - self.x) ** 2
                    + (other.y - self.y) ** 2)

def distance(a: Point, b: Point) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

# A 3-4-5 right triangle
p1, p2 = Point(3, 0), Point(0, 4)
print(p1.distance_to(p2))
#: 5.0
# The method, as a function
print(Point.distance_to(p1, p2))  # [1]
#: 5.0
print(distance(p1, p2))
#: 5.0
```

At `[1]`, `Point.distance_to(p1, p2)` calls the method as if it were a free function.
When you fetch it from the class instead of from an instance,
`distance_to` is an ordinary function,
and the call passes `p1` as the first argument.
`p1.distance_to(p2)` is shorthand for that call.
The dot fills in `self`.

`distance()` has one advantage.
It lives outside `Point`, so it can serve any type that has an `x` and a `y`.
The method keeps one advantage of its own.
Dot-completion on `p1.` lists every operation `Point` supports,
so the method is discoverable.

## Protocols Generalize, Composition Adapts

A function outside any class can work on anything shaped like a point.
A `Protocol` describes that shape.
Any type with matching attributes satisfies it, without inheritance.
That matching is [structural typing](08_Foundations--Static_Types.md#structural-typing-with-protocols).
When someone hands you a type with a different shape,
you adapt it by composition, not inheritance:

```python
# distance_protocol.py
from math import sqrt
from typing import Protocol
from record import record

class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...

def distance(a: Coord, b: Coord) -> float:
    return sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)

@record
class Point:
    x: float
    y: float

@record
class Pair:  # Suppose you are handed this, with no x or y
    a: float
    b: float

# Adapter: uses composition, not inheritance
@record
class PairCoord:
    pair: Pair

    @property
    def x(self) -> float:
        return self.pair.a

    @property
    def y(self) -> float:
        return self.pair.b

print(distance(Point(3, 0), Point(0, 4)))
#: 5.0
print(distance(PairCoord(Pair(3, 0)),
               PairCoord(Pair(0, 4))))
#: 5.0
```

`Point` and `PairCoord` share no base class.
Both have `x` and `y`, and those two attributes are all `distance()` requires.
`PairCoord` is an *Adapter*,
the pattern that [Changing the Interface](29_Patterns--Changing_the_Interface.md#adapter)
covers.

`Coord` declares `x` and `y` as properties rather than as bare `x: float` annotations.
A bare annotation in a protocol is a read-write attribute,
so an implementer must allow assignment to it.
Both classes here keep `x` and `y` read-only.
`PairCoord` computes `x` from its `Pair`,
and the `Point` record rejects assignment to every field.
Both satisfy the property form, and both fail the annotation form.
Declare a protocol member read-only unless callers write to it.

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
print(f"{len(counted)=}, {counted.appends=}")
#: len(counted)=3, counted.appends=1
```

`list.extend()` adds its items and bypasses `append()`,
so the count is wrong the moment anyone adds items through another of the base class's methods.
The subclass is correct line by line.
It inherits an implementation and now depends on that implementation's details.
No signature records that dependence, and no type checker reports it.
That dependence is the *fragile base class* problem:
a base class cannot change its own internals without risking every subclass that came to depend on them.

Composition answers that problem by delegation.
Hold a list instead of being one, and expose only what you meant to expose:

```python
# counting_box.py
from dataclasses import dataclass, field

@dataclass
class CountingBox:
    _items: list[int] = field(default_factory=list)
    appends: int = 0

    def __len__(self) -> int:
        return len(self._items)

    def append(self, item: int) -> None:
        self.appends += 1
        self._items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

box = CountingBox()
box.append(1)
box.extend([2, 3])
print(f"{len(box)=}, {box.appends=}")
#: len(box)=3, box.appends=3
```

`CountingBox` holds its `list` in a field,
so every method that adds items is one it defines.
It writes a forwarding method for each operation it offers.
`CountingList` inherits dozens of methods from `list`,
and more than one of them adds items and bypasses `append()`.

Composition still allows the counting bug.
If you write `extend()` as `self._items.extend(more)` instead of going through `append()`,
the count goes wrong the same way.
What changes is which code holds the bug: the class you read,
not the `list` internals hidden behind `CountingList`.

Composition does more than repair a broken subclass.
A composed type holds other types as fields.
A record built from records compares by value and works as a dict key:

```python
# composition.py
from record import record

@record
class Name:
    first: str
    last: str

@record
class Address:
    city: str
    postal: str

@record
class Contact:
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
# An equal key finds the entry
print({c: "found"}[twin])
#: found
```

`Contact`'s methods are the ones `@record` generates for it.
It holds a `Name` and an `Address`, and those types stay usable on their own.
Value equality and hashing follow from the fields rather than from a base class.

Changing one city means rebuilding the `Address` and then the `Contact`.
[The General Form of `replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
shows `copy.replace()`,
which builds each copy in one call that names only the changed field.

## Polymorphism Without Inheritance

The fourth OOP promise is polymorphism.

### What Is Polymorphism?

Polymorphism means that a function parameter accepts more than one type.
Inheritance is one of several ways to get there.
The questions are which types the parameter accepts and what the function may do with them.

Type theory defines three kinds of polymorphism.
Christopher Strachey's 1967 lecture notes,
[Fundamental Concepts in Programming Languages](http://fpl.cs.depaul.edu/jriely/447/assets/articles/strachey-fundamental-concepts-in-programming-languages.pdf),
named the first two, parametric and ad-hoc.
Cardelli and Wegner added the third, subtyping,
in 1985^[*On Understanding Types, Data Abstraction, and Polymorphism*, where subtyping appears as *inclusion polymorphism*.].

*Subtype polymorphism* means that one function accepts any type that fits a shape.
The four subsections below demonstrate it.
Each subsection defines that shape differently: an `ABC` the type inherits,
a method an `Any` parameter calls at runtime,
a `Protocol` the type matches structurally,
or a union the `match` statement covers.
You write one function.
The argument's type varies from call to call.

*Parametric polymorphism* is a single implementation for multiple types.
[Static Types](08_Foundations--Static_Types.md#type-parameters)'s `first[T]` and `Box[T]` show this.
One body works for any `T`.
The type checker infers the concrete type behind `T` at each call site.

With *ad-hoc polymorphism* (typically *function overloading*),
a different implementation handles each type,
and the argument's type selects which one runs.
One Python form of function overloading is `@overload`.
It gives one function name several typed signatures,
all served by a single implementation that branches at runtime:

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

print(stringify(42))
#: 42
print(stringify([1, 2, 3]))
#: ['1', '2', '3']
```

Each `@overload` line is a declaration for the type checker.
The final `def` is the function that runs.
`stringify(42)` checks as returning `str`,
and `stringify([1, 2, 3])` checks as returning `list[str]`,
although both calls run the same branching body.

[`singledispatch`](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
is ad-hoc polymorphism's other Python form.
It registers a separate function for each type,
instead of one function branching internally.

### Abstract Base Classes

The classic object-oriented example uses an abstract base class:

```python
# shapes_oo.py
import math
from abc import ABC, abstractmethod
from typing import override
from record import record

class Shape(ABC):
    __slots__ = ()

    @abstractmethod
    def area(self) -> float: ...

@record
class Rectangle(Shape):
    length: float
    width: float

    @override
    def area(self) -> float:
        return self.length * self.width

@record
class Circle(Shape):
    radius: float

    @override
    def area(self) -> float:
        return math.pi * self.radius**2

for shape in [Circle(1.0), Rectangle(3.0, 4.0)]:
    print(round(shape.area(), 4))
#: 3.1416
#: 12.0
```

Inheriting from `ABC` and marking `area()` with `@abstractmethod` makes `Shape` abstract.
Calling `Shape()` raises a `TypeError`.
A subclass becomes instantiable when it defines `area()`.

The empty `__slots__` on `Shape` is there for the records that inherit from it.
A base class with no `__slots__` gives every instance of its subclasses a `__dict__`,
the [per-instance dictionary](18_Techniques--Performance.md#when-slots-does-not-fit)
that `@record` exists to remove.
`ABC` declares an empty `__slots__` too,
so the chain stays slotted from `Circle` up to `object`.
The bases in [Changing the Interface](29_Patterns--Changing_the_Interface.md)
and [*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md)
carry the same empty `__slots__` for the same reason.
When a base comes from a library and declares no `__slots__`,
its records use `@record(slots=False)`, which drops slots visibly.
A bare `@record` there declares slots and still gets the base's `__dict__`.

### Dynamic Typing

With dynamic typing,
any type works as long as it has the methods the function calls.
The parameter accepts any argument.
The one validity check comes at runtime, when the call runs:

```python
# dynamic_typing.py
from typing import Any
from exceptions import expect
from record import record

@record
class Bicycle:
    id: str

    def display(self) -> str:
        return f"Bicycle {self.id}"

@record
class Glider:
    size: int

    def display(self) -> str:
        return f"Glider {self.size}"

def show(t: Any) -> str:
    return t.display()

if __name__ == "__main__":
    for item in (Bicycle("Bob"), Glider(65)):
        print(show(item))
    expect(AttributeError, show, 42)
#: Bicycle Bob
#: Glider 65
#: [AttributeError] 'int' object has no attribute 'display'
```

`Any` switches the type checker off for `t`, so any type passes.
Each `Any` parameter is dynamically typed.
`Any` is a different thing from `object`.
If you use `t: object` (the safe top type),
`show()` fails the type checker because `object` has no `display()` method.

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

for item in (Bicycle("Bob"), Glider(65)):
    print(show(item))
#: Bicycle Bob
#: Glider 65
```

A structural type describes the required shape,
and the type checker verifies it ahead of time.
Dynamic typing and protocols both accept any type with a `display()` method.
Dynamic typing finds a missing method when the call runs.
The type checker finds it before the program runs.

An abstract base class is *nominal* (named),
so a type joins by inheriting from it.
The subclass's own source declares membership.
The base can carry shared implementation for its children.
A protocol is structural, so it works with any type that has matching members,
including types in libraries you cannot edit.
The type's author need not hear that your protocol exists.
That independence is why this chapter emphasizes protocols.

The same independence hides membership.
Nothing in a class's own source names the protocols it satisfies,
so you cannot grep a codebase for every type that implements one,
the way you can search for subclasses of a base class.

#### One Class, Many Protocols

Because protocol membership is structural,
one class can satisfy any number of protocols at once,
with no inheritance graph connecting them.
Each protocol describes only the shape it needs.

Classic multiple inheritance has the *diamond problem*.
If two base classes trace back to a common ancestor,
Python resolves which version to call with C3 linearization,
its [method resolution order](07_Foundations--Classes.md#method-resolution-order)
(MRO).
The choice is deterministic,
but a deep hierarchy still makes it easy to lose track of which method runs.
Protocols avoid the question.
With no inheritance graph, C3 has nothing to linearize.
`Invoice`'s three methods satisfy the three protocols:

```python
# multi_protocol.py
import json
from dataclasses import asdict
from typing import Protocol
from record import record

class Priced(Protocol):
    def total(self) -> float: ...

class Serializable(Protocol):
    def to_json(self) -> str: ...

class Describable(Protocol):
    def describe(self) -> str: ...

@record
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

invoice = Invoice(19.99, "Ada")
print(charge(invoice))
#: 19.99
print(persist(invoice))
#: {"amount": 19.99, "customer": "Ada"}
print(audit(invoice))
#: Invoice for Ada
```

`Invoice` inherits from `object` alone, yet `charge()`, `persist()`,
and `audit()` each accept it,
because each function annotates its parameter with a protocol that names the one method the function calls.

#### What the Shape Does Not Say

A protocol's structural check compares member names and types alone.
Two unrelated protocols can share a method name and signature by coincidence.
The checker treats them as interchangeable:

```python
# protocol_collision.py
from typing import Protocol
from record import record

class Priced(Protocol):
    def total(self) -> float: ...

class Weighted(Protocol):
    def total(self) -> float: ...

@record
class Package:
    weight_kg: float

    def total(self) -> float:
        return self.weight_kg  # Weight, not a price

def charge(item: Priced) -> float:
    return item.total()

package = Package(4.5)
print(charge(package))  # Silently treated as a price
#: 4.5
```

The type checker accepts `package` as a `Priced` argument,
and `charge()` returns `4.5`, silently treating a weight as a price.
The shapes do match: `Package.total()` returns a `float`,
as `Priced.total()` declares.
The mismatch is in what the number means.
No type checker verifies meaning.

A distinct type per concept makes the type checker report this mismatch.
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

`UserId` and `int` are different types to the checker.
If `Priced.total()` in `protocol_collision.py` returns a `Price` and `Weighted.total()` returns a `Weight`,
the two protocols declare different return types,
so the type checker can tell `Priced` from `Weighted`.

`NewType` is only an aid during type checking.
At runtime, calling `UserId` returns its argument,
so `UserId(42)` equals `42` and is an `int`:

```python
# test_newtype_boundary.py
from newtype_boundary import UserId

def test_newtype_has_no_runtime_effect() -> None:
    assert UserId(42) == 42
    assert type(UserId(42)) is int
```

Python also accepts a raw `int` where a signature says `UserId`.
At runtime, `lookup(42)` prints `user-42`, the same as `lookup(UserId(42))`.

[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#composing-types-from-types)
takes the other route.
A frozen data class with a validating `__post_init__()` enforces the distinction at runtime too.
Each value then needs a constructor call instead of a bare literal.

A protocol also clarifies what [the Liskov Substitution Principle](#liskov-substitution)
does and does not guarantee.
Satisfying a protocol is a shape claim: the methods exist,
with the correct signatures.
The type checker verifies that half of the contract.
The other half is semantic.
A method must also behave the way callers expect:
return a description rather than raise an exception, finish rather than block,
describe the object rather than change it.
No type checker verifies that half.
Substitution is safe only when both halves hold,
whether membership comes from inheriting a base class or matching a protocol.

### Pattern Matching on a Union

Another approach uses a union and an [exhaustive `match`](13_Techniques--Pattern_Matching.md#exhaustive-matching).
The shapes become immutable data, and one free function handles all the cases,
with no base class and no overridden methods.
The type checker ensures that the match covers every shape.
A `Shape` union and one `area()` function replace the class hierarchy in `shapes_oo.py`:

```python
# shapes_match.py
import math
from typing import assert_never
from record import record

@record
class Rectangle:
    length: float
    width: float

@record
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

shapes: list[Shape] = [Circle(1.0), Rectangle(3.0, 4.0)]
for shape in shapes:
    print(round(area(shape), 4))
#: 3.1416
#: 12.0
```

Adding a new shape is easier in the OOP version,
where the shape is one class that carries its own `area()`,
rather than a record plus a new `case` in every function that matches on shapes.
Adding a new operation over all shapes is easier in the pattern matching
(functional) version,
where the operation is one new function rather than a new method on every class.
In the functional version, the exhaustiveness check covers adding a shape.
Adding a member to the `Shape` union leaves every existing `match` incomplete,
and `assert_never()` turns each one into a type checker error naming the shape you missed.

The OOP approach assumes you add types more often than operations.
That assumption often fails.
This trade-off is the [expression problem](13_Techniques--Pattern_Matching.md#the-expression-problem).
[*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#one-type-or-many)
and [*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
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
    print(total([1.5, 2.5], logger))
    print(logger.lines)
#: 4.0
#: 4.0
#: ['added 1.5, total 1.5', 'added 2.5, total 4.0']
```

The type checker requires the guard.
Without it, `total()` calls `.log()` on `None` and raises an `AttributeError`.
The `None` branch does nothing.
Doing nothing is behavior, and behavior belongs in an object.

The *Null Object* pattern replaces "absent" with an object whose behavior is neutral.
If you give the silent case a class,
an instance of that class replaces `None` as the default:

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

print(total([1.5, 2.5]))
#: 4.0
logger = ListLogger()
print(total([1.5, 2.5], logger))
#: 4.0
print(logger.lines)
#: ['added 1.5, total 1.5', 'added 2.5, total 4.0']
```

`total()` leaves every logging decision to its logger.
`NullLogger` defines silence once, instead of every call site defining it.
Because `NullLogger` is stateless,
one shared `SILENT` instance serves the whole program,
and it is safe as a default argument value.

`Logs` is a protocol, so any logger fits, and no caller sees a `| None`.

The standard library includes this idea as `logging.NullHandler`.
The maze in [Simulation](38_Patterns--Simulation.md)
points every doorless direction at one shared `EDGE` room,
so movement code enters `EDGE` as it enters any other room.

Null objects stand in for "nothing to do," not `None`'s "nothing there."
Sometimes a caller must notice absence,
like a lookup that can fail or a required value that may be missing.
In these cases, use `T | None`,
or return [`Result`](42_Functional--Error_Handling.md#a-result-type),
so the type checker requires callers to handle the missing case.

If every caller handles absence with the same neutral behavior,
centralize that behavior in a null object.
If any caller branches differently, then absence is information,
and it belongs in the type.

## OOP Is Useful, Sometimes

None of this means objects are a mistake.
A class is a clean namespace with dot-completion.
A class guarantees initialization.
As a data class it generates equality and representation,
and hashing when frozen.

OOP also normalized the idea of types,
which [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
takes further.
If you compose instead of inheriting implementation,
the benefit of using types is tremendous.

Start with functions and data.
A program truly needs an object when you find yourself passing the same data into every function,
or bundling behavior with state.
Compare functions and an object on a running balance:

```python
# balance_functions.py
def deposit(balance: float, amount: float) -> float:
    return balance + amount

def withdraw(balance: float, amount: float) -> float:
    return balance - amount

balance = 100.0
balance = deposit(balance, 50.0)
balance = withdraw(balance, 30.0)
print(balance)
#: 120.0
withdraw(balance, 30.0)  # [1]
print(balance)
#: 120.0
```

Every call threads `balance` through,
and every call site must remember to capture the return value.
The call at `[1]` drops its result,
so `balance` keeps its value and prints `120.0` again.
An object stores the balance, so no call site has a result to drop:

```python
# balance_object.py
from dataclasses import dataclass

@dataclass
class Account:
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        self.balance -= amount

account = Account(100.0)
account.deposit(50.0)
account.withdraw(30.0)
print(account.balance)
#: 120.0
```

`deposit()` and `withdraw()` update `self.balance`,
so every call keeps its change.
"Bundling behavior with state" gives you this: one object holds the state,
and the same class defines every method that changes it.
`account.` also lists every operation the object supports through dot-completion.
OOP is useful, sometimes.
But not everywhere, all the time.

## Guidelines

- Prefer immutable data structures over encapsulation.
- Prefer functions over methods.
- Prefer composing structures over inheriting implementation.
- Prefer protocols over a base-class hierarchy.
- Prioritize simplicity, clarity, and maintainability, to produce reliability.

Many of the design patterns in this part of the book arose to work around limitations of older object-oriented languages.
Read those patterns with this chapter's questions in mind.
For each pattern, ask whether you need the objects and the inheritance,
or whether immutable data, a function, and a protocol solve the problem.

## Exercises

Try each exercise before opening its [solution](../Solutions/20_Patterns--Rethinking_Objects/).

1.  In `leaky.py`, add a `tags: list[str]` field to `Leaky`,
    exposed through a `@property` the same way `numbers` is,
    and demonstrate the same leak by mutating the list you get back.
    Then plug the leak the way `plugged.py` plugs `numbers` and `bob`.
2.  In `immutable.py`, remove `frozen=True` from `Bob` and leave it on `Immutable`.
    Show that `ty check` still passes,
    that `immutable.bob.name = "Ralph"` now succeeds,
    and that `hash(immutable)` now raises a `TypeError`,
    so the frozen instance can no longer be a dict key.
    Restore the `frozen=True`.
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
    Confirm `distance()` works on a `TripleCoord` with no change to `distance()`.
5.  In `shapes_match.py`, add a new shape, `Square(side: float)`,
    to the `Shape` union, add its `case` to `area()`,
    and confirm `ty check` still passes.
    Then temporarily comment out the new `case` and observe what `assert_never()` causes the type checker to report.
6.  In `null_logger.py`, write a second null-object style class, `NullCache`,
    whose `get(key)` always returns `None` and whose `set(key, value)` discards the value,
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
    and whether `BoundedStack` should be a subclass of `Stack`.
