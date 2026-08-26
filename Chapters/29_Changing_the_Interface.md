# Changing the Interface

Sometimes the problem you're solving is as simple as "I don't have the interface that I want."
Two of the patterns in *GoF Design Patterns* solve this problem.
*Adapter* takes one type and produces an interface to some other type.
*Façade* creates an interface to a set of classes.
That interface makes a library or bundle of resources more comfortable to use.
Both wrap something that already exists,
which puts them next to Proxy and Decorator,
and a later section sorts the four apart.
Adding an interface is the safe half of the job.
The other half is telling callers that the interface they have been using is going away.

## Adapter

When you've got "this", and you need "that", *Adapter* solves the problem.
The adapter only needs to produce a "that".
The smallest version puts the adaptation in an object of its own:

```python
# adapter.py
# The object adapter.
from typing import override

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    def f(self) -> None: ...

class ProxyAdapter(WhatIWant):
    def __init__(self, what_i_have: WhatIHave) -> None:
        self.what_i_have = what_i_have

    @override
    def f(self) -> None:
        # Implement behavior using
        # methods in WhatIHave:
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

`WhatIUse` calls `f()` and `WhatIHave` has none,
so `ProxyAdapter` supplies one and builds it out of the methods the adaptee does have.
`WhatIWant` is a bare placeholder rather than an ABC or a `Protocol`,
because this listing is about *where* the adaptation lives,
not how you declare the target interface; [Surrogate](26_Surrogate.md#proxy)
compares those two.
The name `ProxyAdapter` takes a liberty with the term "[Proxy](26_Surrogate.md#proxy)":
*GoF Design Patterns* requires a Proxy to have the same interface as the object it speaks for.

The adaptation can live in two other places: the call site,
or the adaptee's own class.

```python
# adapter_variations.py
# Two more places to put the adaptation.
from typing import Any, override
from adapter import ProxyAdapter, WhatIHave, WhatIUse, WhatIWant

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    @override
    def op(self, what_i_have: Any) -> None:
        ProxyAdapter(what_i_have).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    @override
    def f(self) -> None:
        self.g()
        self.h()

WhatIUse2().op(WhatIHave())  # Approach 2: adapting op()
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse().op(WhatIHave2())  # Approach 3: adapter built in
#: WhatIHave.g()
#: WhatIHave.h()
```

The output is deliberately monotonous.
Counting the object adapter above, three structures produce one behavior:
every route ends at the same two methods on a `WhatIHave`.
The approaches differ only in where the adaptation lives.
When the output cannot tell them apart, only packaging separates them.
(GoF adds a fourth placement, an inner-class adapter the adaptee hands out, which is Java packaging for the same forwarding.)

The three split into two families *GoF Design Patterns* names.
`ProxyAdapter` is an *object adapter*:
it holds the adaptee and can wrap any instance handed to it at runtime.
`WhatIHave2` is a *class adapter*: it inherits from the adaptee,
which fixes the adapted class at definition time and exposes the adaptee's entire surface,
`g()` and `h()` included, to every client of the adapter.
Composition keeps the two interfaces separate; inheritance merges them.

The `/` in `WhatIUse.op()` makes its parameter positional-only,
and removing it breaks the override:
`WhatIUse2.op()` renames the parameter to `what_i_have`,
and renaming a keyword-callable parameter in an override breaks substitutability,
so the type checker rejects it without the `/`.
The rename is the smaller half of that story.
`WhatIUse2.op()` also changes the parameter's type.
Its base accepts a `WhatIWant`, and it accepts a `WhatIHave`.
If you annotate both precisely, a type checker rejects the override outright,
reporting `invalid-method-override`,
because narrowing what a method accepts breaks [substitutability](20_Rethinking_Objects.md#liskov-substitution).
That is why this one parameter stays `Any` while the rest of the listing names real types.
The `Any` is not laziness.
It allows an override that cannot substitute for its base to pass the type checker.
Approach 2 is a different operation wearing an inherited name.
Code holding a `WhatIUse` cannot safely receive a `WhatIUse2`,
and that is the price of building the adapter into the operation.
The next section argues Python lets you skip most of this packaging too.

### Adapter in Python

The variations above are Java habits.
At runtime `WhatIUse.op()` only calls `f()`,
so any object with an `f()` works and no shared base class takes part.
A type checker still holds you to the annotation,
so name the requirement with a [`Protocol`](08_Static_Typing.md#structural-typing-with-protocols)
listing `f()` instead of a base class to inherit,
the same substitution [Surrogate](26_Surrogate.md#proxy)
makes for a proxy's implementation.
The common adapter need is "forward most calls unchanged,
and add or change a few."
`__getattr__()` forwards the rest, so the adapter is tiny:

```python
# getattr_adapter.py
from typing import Any

class WhatIHave:
    def g(self) -> str: return "g"
    def h(self) -> str: return "h"

class Adapter:
    def __init__(self, adaptee: WhatIHave) -> None:
        self._adaptee = adaptee

    def f(self) -> str:  # The new interface
        return self._adaptee.g() + self._adaptee.h()

    def __getattr__(self, name: str) -> Any:  # Forwards the rest
        return getattr(self._adaptee, name)

if __name__ == "__main__":
    a = Adapter(WhatIHave())
    print(a.f())  # Adapted method
    print(a.g())  # Forwarded to the adaptee unchanged
#: gh
#: g
```

`__getattr__()` runs only for attributes Python does not find normally,
so `f()` uses the adapter's own version while everything else falls through to the adaptee.
This is the idiomatic Python adapter: a thin wrapper, not a hierarchy.
[Rethinking Objects](20_Rethinking_Objects.md#protocols-generalize-composition-adapts)
has a real one: `PairCoord` adapts a `Pair` to the `Coord` protocol.
It is a frozen dataclass with two properties,
written because the type it received did not fit the function it had to call.
The forwarding carries the limit [Surrogate](26_Surrogate.md#proxy) notes:
special methods bypass `__getattr__()`,
so an adapter that must support `adapter[key]` or `len(adapter)` defines those dunders,
as exercise 1 does with `__getitem__()`.
That chapter's other trap applies here too:
`__getattr__()` reading `self._adaptee` recurses to a `RecursionError` on an instance built without `__init__()`,
which `copy.copy()` and `pickle` do,
so an adapter that must survive copying or pickling defines `__reduce__()` or guards the lookup.

The tests verify both halves of the adapter's behavior.
The new `f()` combines the adaptee's methods,
and calls to methods it doesn't override forward through to the wrapped object:

```python
# test_adapter.py
from getattr_adapter import Adapter, WhatIHave

def test_new_interface_combines_methods() -> None:
    assert Adapter(WhatIHave()).f() == "gh"

def test_getattr_forwards_existing_methods_unchanged() -> None:
    a = Adapter(WhatIHave())
    assert a.g() == "g"
    assert a.h() == "h"

def test_forwarding_targets_the_wrapped_object() -> None:
    have = WhatIHave()
    a = Adapter(have)
    assert a.g.__self__ is have  # __getattr__ delegates to adaptee
```

## Façade

> If something is ugly, hide it inside an object.

That is *Façade*.
If you have a confusing collection of classes and interactions the client programmer doesn't need to see,
create an interface that presents only what's necessary.

A Façade is often a [Singleton](24_Singleton.md)
[Abstract Factory](27_Factory.md#abstract-factories).
A class containing static factory methods gets that effect:

```python
# facade.py
from dataclasses import dataclass

@dataclass(frozen=True)
class A:
    x: object

# Other classes that aren't exposed by the
# facade go here ...

class Facade:
    @staticmethod
    def make_a(x: object) -> A:
        return A(x)

# The client programmer gets the objects
# by calling the static methods:
print(Facade.make_a(1))
#: A(x=1)
```

The cleaner Python façade is a *module*.
A module already presents a curated set of names over whatever tangle of classes lives behind it,
and, as [Singleton](24_Singleton.md#a-module-is-already-a-singleton) notes,
it loads once, and every importer shares the same module.
At module level, put the friendly functions and the few classes to expose.
If you keep the messy internals private
(using a leading underscore, by convention), the `import` is the façade:

```python
# checkout.py
from dataclasses import dataclass

@dataclass(frozen=True)
class _TaxRule:
    rate: float

@dataclass(frozen=True)
class _Discount:
    fraction: float

@dataclass(frozen=True)
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
Three classes and their required assembly order stay behind the underscore,
and the façade can rearrange them without touching a caller.
The underscore is a convention, not a barrier.
`checkout._PriceEngine` still resolves for anyone who types it.
Mechanically, the underscore keeps the name out of `from checkout import *`,
and an [`__all__`](06_Modules_and_Packages.md#what-a-module-exports)
list of the public names states the same boundary explicitly.
A façade is an agreement about which names to call, not a lock on the rest.
A `Facade` class full of static methods only reproduces, with more ceremony,
what a module gives you.

## Telling the Wrappers Apart

Adapter and Façade complete a family of wrappers that share one structure,
a front object forwarding to something behind it,
often through the same few lines of `__getattr__()`.
Intent separates them,
the distinction [The Pattern Concept](21_The_Pattern_Concept.md)
says remains when structures match.
When you cannot decide what to call your wrapper,
ask what breaks if you remove it:

| Wrapper | Interface | What it adds | Remove it and you lose |
| --- | --- | --- | --- |
| [Proxy](26_Surrogate.md#proxy) | same, by GoF's definition | access control | control over when and whether the call gets through |
| [Decorator](14_Decorators.md#the-decorator-pattern) | same | behavior | the added behavior |
| Adapter | changed | nothing | the fit between caller and callee |
| Façade | many narrowed to a few | nothing | the simplicity |

[Surrogate](26_Surrogate.md#proxy) takes the looser view of the first row:
a surrogate speaking for its implementation is a Proxy whether or not the interfaces match.
Under that reading a Proxy becomes an Adapter once you stop insisting on the interface,
which is why the `ProxyAdapter` above answers to both names.
That leaves the "What it adds" column to separate them:
a Proxy controls access to one implementation,
an Adapter makes one type fit a caller that expects another.
Name a wrapper for why it is there, not for its shape.

## Retiring the Old Interface {#retiring-the-old-interface}

Every interface change has a second half.
Once the better interface exists, the old one is still there,
and callers keep using it until something tells them not to.
Deleting it breaks them; leaving it unmarked means nobody notices.
`warnings.deprecated()`
(Python 3.13 and later; `typing_extensions.deprecated` before that)
marks a function, method, or class as on its way out,
and both a type checker and the runtime understand the mark:

```python
# deprecating.py
import warnings

class Report:
    def render(self) -> str:
        return "report"

    @warnings.deprecated("Report.to_string() is replaced by render()")
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
The `# type: ignore` silences `ty`,
which reports the deprecated call as a diagnostic,
the half that reaches a caller before they run anything.
The runtime half is a `DeprecationWarning`.
Python hides those by default outside `__main__` and test runners,
which is the trap: the caller who most needs the warning is the least likely to see it.
Run with `-W default::DeprecationWarning` to see them all,
or `-W error::DeprecationWarning` in continuous integration to fail on one.
A warning also goes to standard error, where a `#:` marker cannot capture it,
so the listing records the warnings and prints the record.

`warnings.deprecated()` requires the message,
and it should say what to use instead.
"Deprecated" tells a reader that someone decided to retire this;
"replaced by `render()`" tells them what to do about it.
The decorator also applies to a class,
where it warns on construction and on subclassing.

The finer instrument is to deprecate a single `@overload`,
warning about one call signature while the rest stay current,
so a function that used to take a string and now takes a `Path` can warn only the string callers.
That form is static only.
Python discards the overload declarations at runtime,
so the `DeprecationWarning` half never fires,
and type-checker support for it lags the whole-function form,
so verify your type checker reports it before relying on it.

An Adapter and a Façade both add an interface without disturbing what is already there,
which is why they are safe moves.
Retiring an interface is the unsafe move,
and marking the old interface is how you make the risk visible on a schedule instead of discovering it when you delete something.

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
4.  Here are three wrappers: one logs each call and forwards it unchanged,
    one exposes a `read()` over an object that only has `next_chunk()`,
    and one refuses calls unless you set a flag.
    Classify each as Proxy, Decorator, Adapter,
    or Façade using the "remove it and you lose" test from the table,
    and say what you would lose in each case.
