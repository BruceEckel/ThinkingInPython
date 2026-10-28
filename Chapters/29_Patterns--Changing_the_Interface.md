# Changing the Interface

> The code you have does the job,
> and the code that needs it expects a different interface.
> *Adapter* and *Façade* supply that interface without changing either side.

Sometimes the problem you're solving is as simple as "I don't have the interface I need."
Two of the patterns in *GoF Design Patterns* solve this problem.
*Adapter* takes one type and produces an interface to some other type.
*Façade* creates an interface to a set of classes.
The caller sees one entry point.
Behind it, the façade creates the objects and connects them to each other,
so the façade's construction code can change while the caller's code stays the same.
*Adapter* and *Façade* both wrap existing code, as *Proxy* and *Decorator* do.

Adding an interface leaves the existing one in place,
so existing callers keep working.
When the new interface replaces one you own,
callers keep using the old one until a deprecation mark tells them to switch.

## Adapter

An adapter's only job is to produce the interface you need from the one you have.
In a common case, a third-party library names its methods `g()` and `h()`,
you wrote your code against an `f()`-calling interface,
and you cannot change either one.
An adapter implements `f()` by calling `g()` and `h()`.
The first version puts the adaptation in a class:

```python
# adapter.py
from typing import override
from record import record

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    __slots__ = ()
    def f(self) -> None: ...

@record
class ProxyAdapter(WhatIWant):
    adaptee: WhatIHave

    @override
    def f(self) -> None:
        print("ProxyAdapter.f()")
        self.adaptee.g()
        self.adaptee.h()

class WhatIUse:
    def op(self, what_i_want: WhatIWant, /) -> None:
        what_i_want.f()

if __name__ == "__main__":
    adapter = ProxyAdapter(WhatIHave())
    WhatIUse().op(adapter)
#: ProxyAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
```

`WhatIWant` is a bare placeholder,
because this listing is about where the adaptation lives.
For declaring the target interface,
[*Surrogate*](25_Patterns--Surrogate.md#what-the-implementation-supplies)
compares an ABC with a `Protocol`.
The empty `__slots__` on `WhatIWant` keeps `ProxyAdapter` a slotted [record](18_Techniques--Performance.md#record),
as `shapes_oo.py` in [Rethinking Objects](20_Patterns--Rethinking_Objects.md#abstract-base-classes)
explains.

The name `ProxyAdapter` uses the term "[*Proxy*](25_Patterns--Surrogate.md#proxy)" loosely.
*GoF Design Patterns* requires a *Proxy* to have the same interface as the object to which it forwards.
`ProxyAdapter` presents `f()` and forwards to an adaptee whose methods are `g()` and `h()`.

### Three Places for the Adaptation

The adaptation can live in two other places:
the method that needs the interface, or a subclass of the adaptee.

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
                print("WhatIUse2.op() wraps it")
                super().op(ProxyAdapter(item))

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    @override
    def f(self) -> None:
        print("WhatIHave2.f()")
        self.g()
        self.h()

WhatIUse2().op(WhatIHave())  # Approach 2
#: WhatIUse2.op() wraps it
#: ProxyAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse2().op(ProxyAdapter(WhatIHave()))
#: ProxyAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse().op(WhatIHave2())  # Approach 3
#: WhatIHave2.f()
#: WhatIHave.g()
#: WhatIHave.h()
```

Counting the *object adapter* in `adapter.py`
(an adapter that wraps an instance of the adaptee),
three structures produce one behavior.
The approaches differ in where the adaptation lives.
The first line of each trace names that place:
`ProxyAdapter.f()` for the object adapter,
`WhatIUse2.op() wraps it` for Approach 2, and `WhatIHave2.f()` for Approach 3.
When `WhatIUse2.op()` receives a `ProxyAdapter`,
the `WhatIWant` branch passes it on as it is,
so that trace opens with `ProxyAdapter.f()`.

*GoF Design Patterns* names two families of adapter.
`ProxyAdapter` is an object adapter.
It holds the adaptee and can wrap any instance passed to it at runtime.
Approach 2 uses the same object adapter and moves the wrapping into `op()`.
`WhatIHave2` is a *class adapter*.
It inherits from the adaptee.
The base-class list specifies the adaptee at definition time.
Every caller of `WhatIHave2` can call every method of the adaptee,
`g()` and `h()` included.
Composition keeps the two interfaces separate.
Inheritance merges them.

GoF describes two further variations.
A *pluggable adapter* is a class with the adaptation built in,
which takes the adapting operations from its client.
A *two-way adapter* presents both interfaces at once,
so code that expects either type accepts it.

### What an Override May Change

The `/` in `WhatIUse.op()` makes its parameter positional-only.
`WhatIUse2.op()` renames that parameter to `item`.
The rename is legal because callers must pass a positional-only parameter by position,
which makes its name private to the method.
If an override renames a keyword-capable parameter,
a call that passes the old name by keyword raises a `TypeError`.
`ty` and Pyright therefore reject that rename in an override
(see exercise 5). mypy accepts it,
because mypy compares the types in an override and ignores the name of any parameter a caller can also pass by position.

The rename is the smaller of the two changes.
`WhatIUse2.op()` also changes the parameter's type,
from `what_i_want: WhatIWant` to `item: WhatIWant | WhatIHave`.
An override may widen what it accepts.
Every call that is legal on a `WhatIUse` is still legal on a `WhatIUse2`,
so code holding a `WhatIUse` can safely receive a `WhatIUse2`.

An override cannot narrow what it accepts.
The commented-out signature in `adapter_variations.py`,
`op(self, item: WhatIHave) -> None`, accepts a `WhatIHave` alone,
the case Approach 2 adds.
If you use that signature in place of the union,
the type checker rejects the override.
A `WhatIUse2` refuses the `WhatIWant` that every `WhatIUse` accepts.
That refusal breaks [substitutability](20_Patterns--Rethinking_Objects.md#liskov-substitution).
`ty` reports the rejection as `invalid-method-override`:

```text
error[invalid-method-override]: Invalid override of
method `op`
info: parameter `what_i_want` has an incompatible type:
`WhatIWant` is not assignable to `WhatIHave`
info: This violates the Liskov Substitution Principle
```

The type checker also reports an `invalid-argument-type` error at `WhatIUse2().op(ProxyAdapter(WhatIHave()))`,
which passes a `ProxyAdapter` where the narrow signature takes a `WhatIHave`.
With the narrow signature,
Approach 2 is a different operation under an inherited name.
The union keeps it the same operation.
Building the adapter into `op()` adds the `WhatIHave` case and leaves the `WhatIWant` case in place.

### Adapter in Python

All three approaches follow one Java habit.
The adapter inherits from `WhatIWant` so that `op()` accepts it.
Because `f()` is the one method `WhatIUse.op()` calls at runtime,
any object with an `f()` works, whatever its base classes.
A type checker still rejects an argument that is not a `WhatIWant`,
so specify the requirement with a [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
that lists `f()`, not with a base class to inherit.
[*Surrogate*](25_Patterns--Surrogate.md#what-the-implementation-supplies)
makes the same substitution for a proxy's implementation.
Here, `WhatIWant` is a `Protocol` that the adapter matches by structure:

```python
# protocol_adapter.py
from typing import Protocol
from adapter import WhatIHave
from record import record

class WhatIWant(Protocol):
    def f(self) -> None: ...

@record
class ObjectAdapter:
    adaptee: WhatIHave

    def f(self) -> None:
        print("ObjectAdapter.f()")
        self.adaptee.g()
        self.adaptee.h()

def use(what_i_want: WhatIWant, /) -> None:
    what_i_want.f()

use(ObjectAdapter(WhatIHave()))
#: ObjectAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
```

`ObjectAdapter` qualifies as a `WhatIWant` because it has an `f()` with the signature the `Protocol` declares.
The adaptee does not qualify.
If you call `use(WhatIHave())`, the type checker rejects the argument,
because `WhatIHave` defines `g()` and `h()`, not `f()`.
`ObjectAdapter` keeps the check that inheritance provides in `adapter.py` and drops the base class.

The standard library declares a target interface of this kind for file paths
(PEP 519, Python 3.6).
`open()`, `pathlib.Path()`,
and the `os` and `os.path` functions accept any object whose `__fspath__()` method returns a `str` or `bytes`.
Defining that one method makes a type of your own acceptable to all of them:

```python
# path_adapter.py
import os
from pathlib import Path
from record import record

@record
class Asset:
    folder: str
    name: str

    def __fspath__(self) -> str:
        return f"{self.folder}/{self.name}"

logo = Asset("images", "logo.svg")
print(isinstance(logo, os.PathLike))
#: True
print(os.path.basename(logo))
#: logo.svg
print(Path(logo).suffix)
#: .svg
```

`Asset` inherits from `object` alone,
yet `isinstance()` reports it as an `os.PathLike`.
At runtime, `os.PathLike` is an abstract base class whose `__subclasshook__()` accepts any class that defines `__fspath__()`.
The type checker treats `os.PathLike` as a `Protocol`,
so `Path(logo)` passes the check.
Each path-taking function passes its argument to `os.fspath()`,
which returns a `str` or `bytes` as it is and calls `__fspath__()` on anything else.

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
#: fffggghhh
#: ggggg
```

Python calls `__getattr__()` as a fallback, after normal attribute lookup fails,
so `f()` uses the adapter's own version while any name the adapter lacks falls through to the adaptee.
`getattr_adapter.py` shows the idiomatic Python adapter: a thin wrapper,
not a hierarchy.
With no base class above it, `Adapter` is a record.

[Rethinking Objects](20_Patterns--Rethinking_Objects.md#protocols-generalize-composition-adapts)
has a real adapter, `PairCoord`, which adapts a `Pair` to the `Coord` protocol.
`PairCoord` is a [record](18_Techniques--Performance.md#record)
with two properties,
written because `distance()` requires `x` and `y` but a `Pair` supplies `a` and `b`.

The limits [*Surrogate*](25_Patterns--Surrogate.md#forwarding-with-getattr)
lists for `__getattr__()` apply to this forwarding too.
[Special methods bypass `__getattr__()`](25_Patterns--Surrogate.md#special-methods-bypass-getattr),
so an adapter that must support `adapter[key]` or `len(adapter)` defines those dunders
(see exercise 1).

[The recursion trap](25_Patterns--Surrogate.md#the-recursion-trap)
applies to an adapter that stores its adaptee in a hand-written `__init__()`.
`copy.copy()` and `pickle` build the new instance without running `__init__()`,
then look up `__setstate__()` on it.
When that lookup fails, Python calls `__getattr__()`,
which reads `self.adaptee`.
No `adaptee` exists yet,
so `__getattr__()` calls itself until Python raises a `RecursionError`.

`Adapter` avoids the trap because it is a record.
A frozen, slotted data class defines `__getstate__()` and `__setstate__()`,
so normal lookup finds `__setstate__()`,
and Python does not call `__getattr__()`.
An adapter written as an ordinary class needs the guard that `getattr_guard.py` in *Surrogate* shows.

The test file confirms that:

- The new `f()` puts its own output in front of the adaptee's `g()` and `h()` results.
- A forwarded method returns what the adaptee's method returns.
- A forwarded method carries the adaptee as its `__self__`.
- A copied adapter still runs `f()`, and an unpickled one still forwards `g()`.

```python
# test_adapter.py
import copy
import pickle
from getattr_adapter import Adapter, WhatIHave

def test_f_puts_its_output_before_g_and_h() -> None:
    assert Adapter(WhatIHave()).f(2) == "ffgghh"

def test_getattr_forwards_existing_methods_unchanged(
) -> None:
    a = Adapter(WhatIHave())
    assert a.g(2) == "gg"
    assert a.h(3) == "hhh"

def test_forwarded_method_is_bound_to_the_adaptee() -> None:
    have = WhatIHave()
    a = Adapter(have)
    assert not hasattr(Adapter, "g")
    assert a.g.__self__ is have

def test_copy_and_pickle_rebuild_the_adapter() -> None:
    a = Adapter(WhatIHave())
    assert copy.copy(a).f(1) == "fgh"
    restored = pickle.loads(pickle.dumps(a))
    assert restored.g(2) == "gg"
```

## Façade

> If something is ugly, hide it inside an object.

That is *Façade*.
If you have a confusing collection of classes and interactions,
create an interface that presents only what the client programmer needs.

A *Façade* is often a [*Singleton*](23_Patterns--Singleton.md)
that also creates the subsystem's objects.
GoF describes both halves of that combination.
One *Façade* object is usually enough, which makes it a *Singleton*.
An [*Abstract Factory*](26_Patterns--Factory.md#abstract-factories)
can work with a *Façade* to create the subsystem's objects without specifying their concrete classes.
When one set of concrete classes is enough,
a class containing static factory methods covers both halves:

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

print(Facade.start_car())
#: Ignition.turn_key()
#: FuelPump.prime()
#: Engine.start()
#: Ignition(pump=FuelPump(engine=Engine()))
```

An `Ignition` holds a `FuelPump` and a `FuelPump` holds an `Engine`,
so a caller builds the three from the inside out,
as `Ignition(FuelPump(Engine()))`.
These three classes are the "confusing collection of classes and interactions,"
small enough here to read at a glance.

In real code, the construction order of three or thirty classes belongs inside the subsystem,
and a façade keeps it there.
`Facade.start_car()` is the static factory method.

The figure shows each pattern as a before-and-after pair:

![](_images/interface_story)

In both pairs, the code you have on the right stays the same.
The difference sits in the middle column.
*Adapter* puts a class there whose `f()` calls `g()` and `h()`,
so the caller keeps calling `f()`.
*Façade* puts a class there that builds the three objects,
so the caller names `Facade` in place of `Ignition`, `FuelPump`, and `Engine`.

The cleaner Python façade is a module.
A module presents a curated set of names over any confusing collection of classes behind it.
As [*Singleton*](23_Patterns--Singleton.md#a-module-is-already-a-singleton)
notes, a module loads once, so every importer shares the same module.
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

The three classes carry leading underscores,
and their required assembly order appears only inside `total()`.
The façade can rearrange both while every caller's code stays the same.

The underscore is a convention,
and `checkout._PriceEngine` resolves for anyone who types it.
Mechanically, `from checkout import *` skips a name with a leading underscore.
An [`__all__`](06_Foundations--Modules_and_Packages.md#what-a-module-exports)
list of the public names makes `from checkout import *` import exactly those names.
A façade is an agreement about which names to call,
not a restriction on the rest.

A `Facade` class full of static methods reproduces what a module gives you,
plus a class statement and a `@staticmethod` on every function.

`checkout.py` is one file.
A façade too large for one file becomes a package.
The package's `__init__.py` re-exports a curated set of names from private submodules.
A leading underscore marks each submodule private,
as it marks the classes in `checkout.py`.
That `__init__.py` is the idiomatic place for a façade to a subsystem of several modules,
GoF's usual case for the pattern.

*Façade* has a failure mode.
An advanced caller who needs a name the façade keeps private has two bad options:
use the underscored name despite the convention,
or wait for the façade's author to expose the name.
If you expose enough names, the façade stops simplifying anything.
It relays every name the subsystem has.

## Distinguishing the Wrappers

*Adapter* and *Façade* complete a family of wrappers with one shared structure:
a front object forwards to something behind it,
often through the same few lines of `__getattr__()`.
[Intent](21_Patterns--Design_Patterns.md#pattern-taxonomy) separates them.
When you cannot decide what to call your wrapper,
ask what breaks if you remove it:

| Wrapper | Interface | What it adds | What removing it loses |
| --- | --- | --- | --- |
| [*Proxy*](25_Patterns--Surrogate.md#proxy) | same, by GoF's definition | access control | control over when and whether the call reaches the implementation |
| [*Decorator*](14_Techniques--Decorators.md#the-decorator-pattern) | same | behavior | the added behavior |
| *Adapter* | changed | nothing | the interface the caller expects |
| *Façade* | many narrowed to a few | nothing | the short list of names a caller needs |

[*Surrogate*](25_Patterns--Surrogate.md#what-the-implementation-supplies)
takes the looser view of the first row:
a surrogate forwarding to its implementation is a *Proxy* whether or not the interfaces match.
Under that reading the same-interface rule no longer separates a *Proxy* from an *Adapter*,
so both names describe the `ProxyAdapter` in `adapter.py`.
That leaves the last two columns to separate them:
a *Proxy* controls access to one implementation,
and an *Adapter* makes one type fit a caller that expects another.
Name a wrapper for why it is there, not for its shape.

## Deprecating the Old Interface {#deprecating-the-old-interface}

Replacing an interface you own takes two steps.
The first is writing the new interface.
Once the new interface exists,
callers keep using the old one until something tells them to switch.
Deleting the old interface breaks those callers.
The second step marks the old interface as deprecated,
which keeps it working and tells each caller to move.

`warnings.deprecated()` marks a function, method,
or class as scheduled for removal
(Python 3.13 and later; `typing_extensions.deprecated` before that).
Both the type checker and the runtime act on the mark:

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
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    print(report.to_string())  # type: ignore
#: report
print(caught[0].category.__name__)
#: DeprecationWarning
print(caught[0].message)
#: Report.to_string() is replaced by render()
```

`to_string()` keeps working,
so existing callers get a warning in place of the `AttributeError` that deleting the method would raise.
The mark works in two halves.
The static half is a `ty` diagnostic on the deprecated call,
which the caller sees before running anything.
The `# type: ignore` silences that diagnostic here,
since this listing calls the deprecated method on purpose.

The runtime half is a `DeprecationWarning`.
Python ignores those by default outside `__main__` and test runners,
so the caller who most needs the warning is the least likely to see it.
Run with `-W default::DeprecationWarning` to see them all,
or `-W error::DeprecationWarning` in continuous integration to fail on one.
A warning meant for the end users of an application takes `category=FutureWarning`,
which Python shows by default.

A warning goes to standard error, but a `#:` marker captures standard output.
`deprecating.py` therefore records the warnings and prints the record.

Much existing code marks a deprecation with a `warnings.warn()` call inside the function body,
with `DeprecationWarning` as the category.
That call supplies the runtime half alone,
since the type checker reads it as an ordinary function call.

`warnings.deprecated()` requires the message.
That message should say what to use instead.
"Deprecated" tells a reader that someone decided callers should stop using this.
"replaced by `render()`" tells them what to do about it.

The decorator also applies to a class,
where it warns on construction and on subclassing.
Applied to a single `@overload`,
the mark deprecates one call signature while the rest stay current.
When a function now takes a `Path` in place of a string,
the mark on the string overload makes the type checker flag each call that still passes a string and accept each call that passes a `Path`.
The mark on an overload is static only.
At runtime every call runs the implementation,
so Python issues no `DeprecationWarning`.
`ty`, Pyright, and mypy all report a deprecated overload.
Pyright and mypy need their deprecation rule enabled,
as they do for the whole-function form.

## Exercises

Try each exercise before opening its [solution](../Solutions/29_Patterns--Changing_the_Interface/).

1.  Write a `PairsAdapter` that wraps a list of `(key, value)` tuples,
    following the shape of `getattr_adapter.py`.
    Give it a dictionary-style `__getitem__()` that finds a value by key,
    and forward every other attribute to the wrapped list with `__getattr__()`.
    Confirm `adapter["name"]` finds a value while `adapter.append(...)` still reaches the underlying list.
    Then call `len(adapter)` and explain the result.
2.  In `deprecating.py`,
    deprecate the whole `Report` class instead of the method,
    and show that constructing a `Report` warns while calling `render()` does not.
3.  Rewrite `facade.py` as a module façade.
    Put its classes behind leading-underscore names in one module,
    expose functions that build them, and import only those from a second file.
    Compare what a caller can see in each version.
4.  Consider three wrappers: one logs each call and forwards it unchanged,
    one exposes a `read()` over an object whose one method is `next_chunk()`,
    and one refuses calls unless you set a flag.
    Classify each as *Proxy*, *Decorator*, *Adapter*,
    or *Façade* using the table's "What removing it loses" column,
    and say what you lose in each case.
5.  Copy the classes from `adapter.py` and remove the `/` from `WhatIUse.op()`.
    Add `WhatIUse2` from `adapter_variations.py` unchanged,
    and call `op()` on each class with the keyword `what_i_want=`.
    Explain what `ty` reports and what each call does at runtime.
    Then fix `WhatIUse2.op()` without restoring the `/`.
