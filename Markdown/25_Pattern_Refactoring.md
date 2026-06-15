# Pattern Refactoring

This chapter follows one problem through several designs. A first solution
solves it, then we ask "what will change?" and reshape the design to absorb that
change cheaply. This is the spirit of Martin Fowler's *Refactoring*, applied at
the level of patterns rather than single statements.

The lesson is also a Python lesson. Several of the patterns that the original
*Design Patterns* book needed are answers to limitations of statically typed
languages without multiple dispatch. Python removes some of those limitations,
so a few famous patterns simply dissolve here. We will call that out as it
happens.

## Simulating the Trash Recycler

Trash arrives at the recycling plant mixed together. The program must sort it by
material and report the total value of each kind. The catch is the one that
makes real problems interesting: the trash starts out as an undifferentiated
pile, and the type of each piece must be recovered to sort it.

Here is the Trash hierarchy. Each material carries a per-pound `value`. Two
small touches make the rest of the chapter easy. The base class keeps a
`registry` of its subclasses, filled automatically by `__init_subclass__`, and
a `create` method builds an instance from a material name. This is the *factory*
the original design worked hard to build with reflection, in a few lines and
with no reflection at all:

```python
# trash.py
# The Trash hierarchy, with self-registration and a per-pound value.
from __future__ import annotations


class Trash:
    value: float = 0.0  # dollars per pound, set by each subclass
    registry: dict[str, type[Trash]] = {}  # name -> subclass

    def __init__(self, weight: float) -> None:
        self.weight = weight

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return Trash.registry[name](weight)


class Aluminum(Trash):
    value = 1.67


class Paper(Trash):
    value = 0.10


class Glass(Trash):
    value = 0.23


class Cardboard(Trash):
    value = 0.79


def sum_value(items: list[Trash]) -> float:
    total = 0.0
    for t in items:
        print(f"weight of {type(t).__name__} = {t.weight}")
        total += t.weight * t.value
    print(f"Total value = {total:.2f}")
    return total
```

Adding a new material is now one class definition. It registers itself, and
`create` can build it. `sum_value` is an ordinary function: it relies on
polymorphism (`t.value`, `t.weight`) and never asks what type each piece is.

The trash to process is described in a data file, one `Name:weight` line per
piece:

```python
# Trash.dat
Glass:54
Paper:22
Paper:11
Glass:17
Aluminum:89
Paper:88
Aluminum:76
Cardboard:96
Aluminum:25
Aluminum:34
Glass:11
Glass:68
Glass:43
Aluminum:27
Cardboard:44
Aluminum:18
Paper:91
Glass:63
Glass:50
Glass:80
Aluminum:81
Cardboard:12
```

Parsing it into `Trash` objects goes through the registry, so the parser never
mentions a concrete material. Add a new kind of trash and the parser keeps
working unchanged, which is the sign of a good seam:

```python
# parse_trash.py
# Read "Name:weight" lines into Trash objects through the registry.
from trash import Trash


def parse(filename: str) -> list[Trash]:
    items: list[Trash] = []
    with open(filename) as source:
        for line in source:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, weight = line.split(":")
            items.append(Trash.create(name.strip(), float(weight)))
    return items
```

## The First Cut: Checking Every Type

The most obvious way to sort is to look at each piece and test what it is. The
original design used run-time type information (RTTI) for this, and so can we
with `isinstance`:

```python
# recycle_rtti.py
# First cut: sort by testing each type. It works, but it checks for
# EVERY type. Add a new kind of Trash and you must find and edit
# this code, with no help from the tools if you miss a spot. That is
# the smell to watch for.
from collections import defaultdict

from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Paper, Trash, sum_value


def main() -> None:
    bins: dict[type, list[Trash]] = defaultdict(list)
    for t in parse("Trash.dat"):
        if isinstance(t, Aluminum):
            bins[Aluminum].append(t)
        elif isinstance(t, Paper):
            bins[Paper].append(t)
        elif isinstance(t, Glass):
            bins[Glass].append(t)
        elif isinstance(t, Cardboard):
            bins[Cardboard].append(t)
    for kind, items in bins.items():
        print(f"--- {kind.__name__} ---")
        sum_value(items)


if __name__ == "__main__":
    main()
```

This satisfies the requirement, but it has the classic flaw. It tests for *every
type in the system*. When cardboard becomes valuable and you add it, you must
hunt down this chain of `isinstance` checks, and any you miss will silently drop
trash on the floor. Testing for one type, or a small subset that needs special
handling, is fine. Testing for all of them means you are doing by hand the job
that polymorphism exists to do for you.

## Let a Dictionary Do the Sorting

The original chapter spent several designs removing this RTTI: a hierarchy of
typed bins, then "double dispatch," each adding classes to push the type
decision into the language. In Python the whole problem disappears with one
line. Group the pieces in a dictionary keyed by their own type:

```python
# recycle_dict.py
# The Pythonic sort: the object's own type is the key. No type is
# named here, so this code never changes when you add a new kind of
# Trash.
from collections import defaultdict

from parse_trash import parse
from trash import Trash, sum_value


def main() -> None:
    bins: dict[type, list[Trash]] = defaultdict(list)
    for t in parse("Trash.dat"):
        bins[type(t)].append(t)  # bin chosen by the piece itself
    for kind, items in bins.items():
        print(f"--- {kind.__name__} ---")
        sum_value(items)


if __name__ == "__main__":
    main()
```

`type(t)` is the perfect key: it adapts to whatever types show up, even ones
added at run time. There is no chain to maintain and nothing to forget. This is
the same idea the original reached only at the very end of the chapter, as a
`HashMap` of typed lists. Here it is the natural first thing a Python programmer
writes.

## Adding Operations: Visitor, and Why Python Skips It

So far we have changed *types* cheaply. The other axis of change is adding new
*operations*. Suppose the `Trash` hierarchy is fixed (maybe it ships from a
vendor) and you want to add new behaviors to it without editing it: price it,
weigh it, print recycling instructions, and more later.

This is exactly the problem the *Visitor* pattern was invented for. Visitor is
elaborate: a `Visitor` base class with one `visit` overload per material, an
`accept` method added to every element, and "double dispatch" to route each
piece to the right `visit`. It exists because languages like Java and C++
dispatch on only one type at a time and cannot add methods to a class from
outside. Python has neither limitation in this case, because the standard
library provides `functools.singledispatch`: a function that dispatches on the
type of its first argument, with new types registered from anywhere.

So you do not write Visitor in Python. You write a single-dispatch function:

```python
# visitor_singledispatch.py
# Visitor's goal is to add operations to a fixed hierarchy from
# outside it. functools.singledispatch does that directly: a
# polymorphic function whose behavior is registered per type. Trash
# is never touched, new operations are independent functions, and
# new types just register themselves.
from functools import singledispatch

from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Trash


@singledispatch
def recycling_note(t: Trash) -> str:
    return f"{type(t).__name__}: no special handling"


@recycling_note.register
def _(t: Aluminum) -> str:
    return "Aluminum: crush and bale"


@recycling_note.register
def _(t: Glass) -> str:
    return "Glass: sort by color, then crush"


@recycling_note.register
def _(t: Cardboard) -> str:
    return "Cardboard: flatten and bundle"


def main() -> None:
    seen: set[type] = set()
    for t in parse("Trash.dat"):
        if type(t) not in seen:
            seen.add(type(t))
            print(recycling_note(t))


if __name__ == "__main__":
    main()
```

Compare this to a Visitor implementation. There is no `Visitor` class, no
`accept` method bolted onto every material, and no decorator gymnastics to fake
overloading. `recycling_note` is a new operation defined entirely outside the
`Trash` hierarchy, which is Visitor's whole purpose. `Paper` has no registered
note, so it falls through to the base function: the default behavior, for free.
Adding a `price` or `weight` operation means writing another single-dispatch
function. Adding a `Plastic` material means defining the class and, if it needs
a special note, registering one line.

When the operation is the *same* for every type, you do not even need
single dispatch. `sum_value` earlier was just a function. Reach for
`singledispatch` only when the behavior genuinely differs by type. For
operations that belong on the objects and vary by type, `singledispatchmethod`
does the same thing as a method.

## Summary

Watching this problem evolve, notice which patterns survived the move to Python
and which dissolved:

- The *Factory* survived, but shrank. Self-registration through
  `__init_subclass__` plus a name-keyed `registry` replaced an entire
  reflection-based prototyping scheme. Adding a type is one class definition.
- The typed-bin hierarchy and *double dispatch* dissolved. A `dict` keyed by
  `type(piece)` sorts anything and never needs editing.
- *Visitor* dissolved into `functools.singledispatch`. The pattern is largely a
  workaround for languages that lack multiple dispatch and open methods; Python
  supplies both, so the ceremony is unnecessary.

Design patterns are about *separating what changes from what stays the same*.
Polymorphism is one way to do that, and the most important one, but it is not the
only one. The deeper skill is spotting the "vector of change" in a problem (here,
new types versus new operations) and choosing the lightest construct that
isolates it. In Python that construct is often a language feature, not a
multi-class pattern. The honest measure of a pattern is whether it still earns
its keep once the language does part of the work for you.

## Exercises

1.  Add a `Plastic` material with a per-pound value. Confirm that
    `recycle_dict.py` and `parse_trash.py` need no changes, and that only
    `Trash.dat` and (optionally) a one-line `recycling_note` registration do.
2.  Write a `price` operation as a plain function over a list of `Trash`, and a
    `heaviest` operation that returns the single heaviest piece. Decide for each
    whether it needs `singledispatch`.
3.  Replace the `recycling_note` single-dispatch function with a
    `singledispatchmethod` on a `Sorter` class, and explain what changed.
