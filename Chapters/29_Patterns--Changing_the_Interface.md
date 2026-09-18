# Changing the Interface

Sometimes the problem you're solving is as simple as "I don't have the interface I need."
Two of the patterns in *GoF Design Patterns* solve this problem.
*Adapter* takes one type and produces an interface to some other type.
*Façade* creates an interface to a set of classes.
The caller sees one entry point and never learns how those classes are built and wired together,
so the wiring can change without affecting the caller.
Both wrap something that already exists,
which puts them adjacent to *Proxy* and *Decorator*.
Adding an interface leaves the existing one in place, so nothing breaks.
When the new interface is meant to replace one you own,
callers keep using the old one until you mark it deprecated.

## Adapter

An adapter's only job is to produce the interface you need from the one you have.
A common real case: a third-party library names its methods `g()` and `h()`,
you wrote your code against an `f()`-calling interface,
and you cannot change either one.
An adapter sits between them and fixes the problem.
The first version uses a class to perform adaptation:

```python
# adapter.py
from dataclasses import dataclass
from typing import override

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    def f(self) -> None: ...

@dataclass(frozen=True)
class ProxyAdapter(WhatIWant):
    what_i_have: WhatIHave

    @override
    def f(self) -> None:
        # Implement behavior using WhatIHave:
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want: WhatIWant, /) -> None:
        what_i_want.f()

if __name__ == "__main__":
    adapt = ProxyAdapter(WhatIHave())
    WhatIUse().op(adapt)
#: WhatIHave.g()
#: WhatIHave.h()
```

Because `WhatIUse` calls `f()` and `WhatIHave` has no `f()`,
`ProxyAdapter` supplies one and builds it out of the methods the adaptee does have.
`WhatIWant` is a bare placeholder rather than an ABC or a `Protocol`,
because this listing is about *where* the adaptation lives,
not how you declare the target interface.
[*Surrogate*](26_Patterns--Surrogate.md#proxy)
compares an ABC with a `Protocol`.
`WhatIWant` declares no `__slots__`,
so `ProxyAdapter` is declared with `@dataclass(frozen=True)` and not `@record`:
an unslotted base gives each instance its `__dict__` back
([Performance](18_Techniques--Performance.md#record)).
The name `ProxyAdapter` uses the term "[*Proxy*](26_Patterns--Surrogate.md#proxy)" loosely:
*GoF Design Patterns* requires a *Proxy* to have the same interface as the object it forwards to.

The adaptation can live in two other places: the call site,
or the adaptee's own class.

```python
# adapter_variations.py
from typing import override
from adapter import (ProxyAdapter, WhatIHave, WhatIUse,
                     WhatIWant)

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    @override
    # With WhatIHave alone, ty rejects the override:
    # def op(self, item: WhatIHave) -> None:
    def op(self, item: WhatIWant | WhatIHave) -> None:
        match item:
            case WhatIWant():
                super().op(item)
            case WhatIHave():
                ProxyAdapter(item).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    @override
    def f(self) -> None:
        self.g()
        self.h()

WhatIUse2().op(WhatIHave())  # Approach 2
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse2().op(ProxyAdapter(WhatIHave()))
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse().op(WhatIHave2())  # Approach 3
#: WhatIHave.g()
#: WhatIHave.h()
```

Counting the object adapter in `adapter.py`,
three structures produce one behavior:
each approach calls the same two methods on a `WhatIHave`.
The approaches differ only in where the adaptation lives.
When the output is the same for every approach, only packaging separates them.
(GoF varies the same forwarding two further ways: a *pluggable adapter* takes the adapting operation as a delegate the client supplies, and a *two-way adapter* presents both interfaces at once.)

*GoF Design Patterns* splits the three approaches into two families.
`ProxyAdapter` is an *object adapter*:
it holds the adaptee and can wrap any instance passed to it at runtime.
`WhatIHave2` is a *class adapter*: it inherits from the adaptee.
That inheritance fixes the adapted class at definition time,
and every client of the adapter can call every method of the adaptee,
`g()` and `h()` included.
Composition keeps the two interfaces separate.
Inheritance merges them.

The `/` in `WhatIUse.op()` makes its parameter positional-only.
`WhatIUse2.op()` renames that parameter to `item`.
The rename is legal because callers cannot use a positional-only parameter name.
Renaming a keyword-capable parameter would break any caller passing it by keyword,
so `ty` rejects a renamed keyword-capable parameter in an override.
A checker that accepts such a rename compares the types in an override and skips the parameter names.

The rename is the smaller of the two changes.
`WhatIUse2.op()` also changes the parameter's type.
The base version accepts a `WhatIWant`,
and the override accepts a `WhatIWant` or a `WhatIHave`.
An override may widen what it accepts.
Every call that is legal on a `WhatIUse` is still legal on a `WhatIUse2`,
so code holding a `WhatIUse` can safely receive a `WhatIUse2`.
The `match` passes a `WhatIWant` to the inherited `op()` and adapts a `WhatIHave`.

An override cannot narrow what it accepts.
The commented-out signature in `adapter_variations.py` takes a `WhatIHave` alone,
which is all Approach 2 needs for its own callers.
If you use that signature in place of the union,
a type checker rejects the override:
a `WhatIUse2` would refuse the `WhatIWant` that every `WhatIUse` accepts,
and that breaks [substitutability](20_Patterns--Rethinking_Objects.md#liskov-substitution).
`ty` reports the rejection as `invalid-method-override`:

```text
error[invalid-method-override]: Invalid override of
method `op`
info: parameter `what_i_want` has an incompatible type:
`WhatIWant` is not assignable to `WhatIHave`
info: This violates the Liskov Substitution Principle
```

`ty` reports a second error at the listing's second call,
which passes a `ProxyAdapter` where the narrow signature takes a `WhatIHave`.
With the narrow signature,
Approach 2 is a different operation under an inherited name.
The union keeps it the same operation:
building the adapter into `op()` adds the `WhatIHave` case and leaves the `WhatIWant` case in place.

### Adapter in Python

All three approaches carry one Java habit:
the adapter inherits from `WhatIWant` so that `op()` accepts it.
Because at runtime `WhatIUse.op()` calls only `f()`,
any object with an `f()` works and no shared base class takes part.
A type checker still enforces the annotation,
so name the requirement with a [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
that lists `f()`, not with a base class to inherit.
[*Surrogate*](26_Patterns--Surrogate.md#proxy)
makes the same substitution for a proxy's implementation.

The common adapter need is "forward most calls unchanged,
and add or change a few."
`__getattr__()` forwards the rest, so the adapter is tiny:

```python
# getattr_adapter.py
from typing import Any
from record import record

class WhatIHave:
    def g(self, n: int) -> str: return "g" * n
    def h(self, n: int) -> str: return "h" * n

@record
class Adapter:
    adaptee: WhatIHave

    def f(self, n: int) -> str:  # The new interface
        return ("f" * n +
            self.adaptee.g(n) + self.adaptee.h(n))

    # Forward the rest
    def __getattr__(self, name: str) -> Any:
        return getattr(self.adaptee, name)

if __name__ == "__main__":
    a = Adapter(WhatIHave())
    print(a.f(3))  # Adapted method
    print(a.g(5))  # Forwarded to the adaptee unchanged
    print(a.h(7))
#: fffggghhh
#: ggggg
#: hhhhhhh
```

Because `__getattr__()` runs only for attributes Python does not find normally,
`f()` uses the adapter's own version while everything else falls through to the adaptee.
This is the idiomatic Python adapter: a thin wrapper, not a hierarchy.
With no base class above it, `Adapter` is a record.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#protocols-generalize-composition-adapts)
has a real one: `PairCoord` adapts a `Pair` to the `Coord` protocol.
It is a [record](18_Techniques--Performance.md#record) with two properties,
written because `distance()` requires `x` and `y` but a `Pair` supplies `a` and `b`.

The limits [*Surrogate*](26_Patterns--Surrogate.md#forwarding-with-getattr)
lists for `__getattr__()` apply to this forwarding too.
[Special methods bypass it](26_Patterns--Surrogate.md#special-methods-bypass-getattr),
so an adapter that must support `adapter[key]` or `len(adapter)` defines those dunders,
as exercise 1 does with `__getitem__()`.

[The recursion trap](26_Patterns--Surrogate.md#the-recursion-trap)
applies here too.
Because `copy.copy()` and `pickle` build an instance without running `__init__()`,
`adaptee` does not exist yet.
`__getattr__()` reading `self.adaptee` then calls itself until Python raises a `RecursionError`.
An adapter that must survive copying or pickling guards that lookup,
or defines `__reduce__()`,
the hook `pickle` and `copy` consult before ordinary construction.

Testing confirms that the new `f()` puts its own output in front of the adaptee's `g()` and `h()` results,
and every other call forwards to the wrapped object:

```python
# test_adapter.py
from getattr_adapter import Adapter, WhatIHave

def test_new_interface_combines_methods() -> None:
    assert Adapter(WhatIHave()).f(2) == "ffgghh"

def test_getattr_forwards_existing_methods_unchanged(
) -> None:
    a = Adapter(WhatIHave())
    assert a.g(2) == "gg"
    assert a.h(3) == "hhh"

def test_forwarding_targets_the_wrapped_object() -> None:
    have = WhatIHave()
    a = Adapter(have)
    # __getattr__ delegates to adaptee
    assert a.g.__self__ is have
```

## Façade

> If something is ugly, hide it inside an object.

That is *Façade*.
If you have a confusing collection of classes and interactions,
create an interface that presents only what the client programmer needs.

A *Façade* is often a [*Singleton*](24_Patterns--Singleton.md)
[*Abstract Factory*](27_Patterns--Factory.md#abstract-factories).
A class containing static factory methods gets that effect:

```python
# facade.py
from record import record

@record
class Engine:
    def start(self) -> None:
        print("Engine.start()")

@record
class FuelPump:
    engine: Engine

    def prime(self) -> None:
        print("FuelPump.prime()")
        self.engine.start()

@record
class Ignition:
    pump: FuelPump

    def turn_key(self) -> None:
        print("Ignition.turn_key()")
        self.pump.prime()

class Facade:
    @staticmethod
    def start_car() -> Ignition:
        ignition = Ignition(FuelPump(Engine()))
        ignition.turn_key()
        return ignition

Facade.start_car()
#: Ignition.turn_key()
#: FuelPump.prime()
#: Engine.start()
```

Turning the key primes the pump, and priming starts the engine.
`Ignition` needs `FuelPump`, and `FuelPump` needs `Engine`, in that order,
or the call sequence is wrong.
That is the "confusing collection of classes and interactions,"
small enough to read in one glance here.
In real code, constructing three or thirty classes in the right order is knowledge a caller should never need.
`Facade.start_car()` hides the constructor calls and their order behind one call that also builds the object,
the "static factory method" GoF pairs with *Façade*.

The cleaner Python façade is a *module*.
A module already presents a curated set of names over any confusing collection of classes behind it.
As [*Singleton*](24_Patterns--Singleton.md#a-module-is-already-a-singleton)
notes, it loads once, and every importer shares the same module.
At module level, put the convenient functions and the few classes to expose.
If you keep the messy internals private
(using a leading underscore, by convention), the `import` is the façade:

```python
# checkout.py
from record import record

@record
class _TaxRule:
    rate: float

@record
class _Discount:
    fraction: float

@record
class _PriceEngine:
    tax: _TaxRule
    cut: _Discount

    def compute(self, amount: float) -> float:
        net = amount * (1 - self.cut.fraction)
        return net * (1 + self.tax.rate)

def total(amount: float) -> float:
    engine = _PriceEngine(_TaxRule(0.08), _Discount(0.10))
    return engine.compute(amount)
```

```python
# checkout_demo.py
import checkout

print(f"{checkout.total(100.0):.2f}")
#: 97.20
```

The caller imports one name.
The three classes carry leading underscores,
and their required assembly order appears only inside `total()`.
The façade can rearrange both while every caller's code stays the same.

The underscore is a convention; Python does not enforce it.
`checkout._PriceEngine` still resolves for anyone who types it.
Mechanically, the underscore keeps the name out of `from checkout import *`,
and an [`__all__`](06_Foundations--Modules_and_Packages.md#what-a-module-exports)
list of the public names states the same boundary explicitly.
A façade is an agreement about which names to call,
not a restriction on the rest.

A `Facade` class full of static methods reproduces only what a module gives you,
with more ceremony.
`checkout.py` is one file; a façade that outgrows one file scales the same way,
one level up.
A package's `__init__.py` re-exports a curated set of names from private submodules,
the same underscore convention, applied to modules instead of classes.
That is the idiomatic place for a façade that fronts a whole subsystem several modules deep,
GoF's usual case for the pattern.

*Façade* has a failure mode too.
An advanced caller who needs a name the façade never exposed has two bad options:
use the underscored name despite the convention,
or wait for the façade's author to expose the name.
If you expose enough names, the façade stops simplifying anything;
it relays every name the subsystem has.

## Distinguishing the Wrappers

*Adapter* and *Façade* complete a family of wrappers that share one structure,
a front object forwarding to something behind it,
often through the same few lines of `__getattr__()`.
Intent separates them; [Design Patterns](21_Patterns--Design_Patterns.md)
says that distinction remains when structures match.
When you cannot decide what to call your wrapper,
ask what breaks if you remove it:

| Wrapper | Interface | What it adds | Remove it and you lose |
| --- | --- | --- | --- |
| [*Proxy*](26_Patterns--Surrogate.md#proxy) | same, by GoF's definition | access control | control over when and whether the call reaches the implementation |
| [*Decorator*](14_Techniques--Decorators.md#the-decorator-pattern) | same | behavior | the added behavior |
| *Adapter* | changed | nothing | the fit between caller and callee |
| *Façade* | many narrowed to a few | nothing | the simplicity |

[*Surrogate*](26_Patterns--Surrogate.md#proxy)
takes the looser view of the first row:
a surrogate forwarding to its implementation is a *Proxy* whether or not the interfaces match.
Under that reading the same-interface rule no longer separates a *Proxy* from an *Adapter*,
which is why the `ProxyAdapter` in `adapter.py` answers to both names.
That leaves the "What it adds" column to separate them:
a *Proxy* controls access to one implementation,
an *Adapter* makes one type fit a caller that expects another.
Name a wrapper for why it is there, not for its shape.

## Deprecating the Old Interface {#deprecating-the-old-interface}

An interface that replaces one you own has a second half.
Once the better interface exists, the old one is still there,
and callers keep using it until something tells them not to.
Deleting it breaks them.
Leaving it unmarked means nobody notices.
`warnings.deprecated()` marks a function, method,
or class as scheduled for removal
(Python 3.13 and later; `typing_extensions.deprecated` before that).
Both a type checker and the runtime act on the mark:

```python
# deprecating.py
import warnings

class Report:
    def render(self) -> str:
        return "report"

    @warnings.deprecated(
        "Report.to_string() is replaced by render()")
    def to_string(self) -> str:
        return self.render()

report = Report()
print(report.render())
#: report
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    print(report.to_string())  # type: ignore
#: report
print(caught[0].category.__name__)
#: DeprecationWarning
print(caught[0].message)
#: Report.to_string() is replaced by render()
```

`to_string()` keeps working, which is the point: existing callers get a warning,
not a break.
The mark works in two halves.
The static half is a `ty` diagnostic on the deprecated call,
and the caller sees it before running anything.
The `# type: ignore` silences that diagnostic here,
since this listing calls the deprecated method on purpose.
The runtime half is a `DeprecationWarning`.
Python ignores those by default outside `__main__` and test runners,
which is the trap: the caller who most needs the warning is the least likely to see it.
Run with `-W default::DeprecationWarning` to see them all,
or `-W error::DeprecationWarning` in continuous integration to fail on one.
A warning also goes to standard error, where a `#:` marker cannot capture it,
so the listing records the warnings and prints the record.

`warnings.deprecated()` requires the message,
and that message should say what to use instead.
"Deprecated" tells a reader that someone decided this should no longer be called.
"replaced by `render()`" tells them what to do about it.

The decorator also applies to a class,
where it warns on construction and on subclassing.
Applied to a single `@overload`,
the mark deprecates one call signature while the rest stay current.
A function that now takes a `Path` in place of a string can then warn only the callers still passing a string.
That form is static only.
Python discards the overload declarations at runtime and never issues the `DeprecationWarning`.
`ty`, Pyright, and mypy all report a deprecated overload.
Pyright and mypy need their deprecation rule switched on,
as they do for the whole-function form.

An *Adapter* and a *Façade* both add an interface and leave what is already there in place,
which is why they are safe moves.
Replacing an interface you own is the unsafe move,
because every caller was written against the old one.
Marking it deprecated keeps it working while it tells each caller what to use instead;
without the mark, nothing tells them.

## Exercises

1.  Write a `PairsAdapter` that wraps a list of `(key, value)` tuples,
    following the shape of `getattr_adapter.py`.
    Give it a dictionary-style `__getitem__()` that finds a value by key,
    and forward every other attribute to the wrapped list with `__getattr__()`.
    Confirm `adapter["name"]` finds a value while `adapter.append(...)` still reaches the underlying list.
2.  In `deprecating.py`,
    deprecate the whole `Report` class instead of the method,
    and show that constructing a `Report` warns while calling `render()` does not.
3.  Rewrite `facade.py` as a module façade.
    Put its classes behind leading-underscore names in one module,
    expose functions that build them, and import only those from a second file.
    Compare what a caller can see in each version.
4.  Consider three wrappers, described in words rather than code:
    one logs each call and forwards it unchanged,
    one exposes a `read()` over an object that has only `next_chunk()`,
    and one refuses calls unless you set a flag.
    Classify each as *Proxy*, *Decorator*, *Adapter*,
    or *Façade* using the "remove it and you lose" test from the table,
    and say what you would lose in each case.
