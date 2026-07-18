# Changing the Interface

Sometimes the problem you're solving is as simple as "I don't have the interface that I want."
Two of the patterns in *GoF Design Patterns* solve this problem.
*Adapter* takes one type and produces an interface to some other type.
*Façade* creates an interface to a set of classes,
providing a more comfortable way to deal with a library or bundle of resources.

## Adapter

When you've got *this*, and you need *that*, *Adapter* solves the problem.
The only requirement is to produce a *that*,
and there are a number of ways to accomplish this adaptation:

```python
# adapter.py
# Variations on the Adapter pattern.
from typing import Any, override

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    def f(self) -> None: ...

class ProxyAdapter(WhatIWant):
    def __init__(self, what_i_have: Any) -> None:
        self.what_i_have = what_i_have

    @override
    def f(self) -> None:
        # Implement behavior using
        # methods in WhatIHave:
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want: Any, /) -> None:
        what_i_want.f()

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

# Approach 4: use an inner class:
class WhatIHave3(WhatIHave):
    class InnerAdapter(WhatIWant):
        def __init__(self, outer: Any) -> None:
            self.outer = outer
        @override
        def f(self) -> None:
            self.outer.g()
            self.outer.h()

    def what_i_want(self) -> WhatIWant:
        return WhatIHave3.InnerAdapter(self)

what_i_use = WhatIUse()
what_i_have = WhatIHave()
adapt = ProxyAdapter(what_i_have)
what_i_use2 = WhatIUse2()
what_i_have2 = WhatIHave2()
what_i_have3 = WhatIHave3()
what_i_use.op(adapt)  # Approach 1: separate adapter
#: WhatIHave.g()
#: WhatIHave.h()
what_i_use2.op(what_i_have)  # Approach 2: adapting op()
#: WhatIHave.g()
#: WhatIHave.h()
what_i_use.op(what_i_have2)  # Approach 3: adapter built in
#: WhatIHave.g()
#: WhatIHave.h()
what_i_use.op(what_i_have3.what_i_want())  # Approach 4
#: WhatIHave.g()
#: WhatIHave.h()
```

The output is deliberately monotonous.
Four different structures produce one behavior:
every route ends at the same two methods on a `WhatIHave`.
The approaches differ only in where the adaptation lives, a separate object,
the call site, the adaptee's own class, or an inner class the adaptee hands out.
When the output cannot tell the approaches apart,
the choice among them is purely one of packaging,
and the next section argues Python lets you skip most of the packaging too.

This takes liberty with the term "[Proxy](26_Surrogate.md#proxy),"
because *GoF Design Patterns* asserts that a Proxy must have an identical interface with the object for which it is a surrogate.

Two details in the listing repay attention.
The `/` in `WhatIUse.op()` makes its parameter positional-only,
and it is load-bearing: `WhatIUse2.op()` renames the parameter to `what_i_have`,
and renaming a keyword-callable parameter in an override breaks substitutability,
so the checker rejects it without the `/`.
Second, the approaches split into two families *GoF Design Patterns* names.
`ProxyAdapter` is an *object adapter*:
it holds the adaptee and can wrap any instance handed to it at runtime.
`WhatIHave2` is a *class adapter*: it inherits from the adaptee,
which fixes the adapted class at definition time and exposes the adaptee's entire surface,
`g()` and `h()` included, to every client of the adapter.
Composition keeps the two interfaces separate; inheritance merges them.

### Adapter in Python

The four variations above are Java habits.
Python is dynamically typed.
`WhatIUse.op()` only calls `f()`, so it accepts any object that has an `f()`.
You do not need a shared base class or a declared interface, only the method.
The common adapter need is "forward most calls unchanged,
and add or change a few."
`__getattr__()` does the forwarding, so the adapter is tiny:

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

a = Adapter(WhatIHave())
print(a.f())  # Adapted method
#: gh
print(a.g())  # Forwarded to the adaptee unchanged
#: g
```

`__getattr__()` runs only for attributes Python does not find normally,
so `f()` uses the adapter's own version while everything else falls through to the adaptee.
This is the idiomatic Python adapter: a thin wrapper, not a hierarchy.
You have already seen one in earnest:
`PairCoord` in [Rethinking Objects](20_Rethinking_Objects.md#protocols-generalize-composition-adapts)
adapts a `Pair` to the `Coord` protocol,
an adapter as a frozen dataclass with two properties,
built precisely because the handed-to-you type did not fit.
The forwarding has the limit noted in [Surrogate](26_Surrogate.md#proxy):
special methods bypass `__getattr__()`,
so an adapter that must support `adapter[key]` or `len(adapter)` defines those dunders itself,
as exercise 1 does with `__getitem__()`.

Testing verifies both halves of that behavior.
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

That is what *Façade* accomplishes.
If you have a confusing collection of classes and interactions that the client programmer doesn't really need to see,
then you can create an interface that is useful for the client programmer and that only presents what's necessary.

A Façade often takes the form of a [Singleton](24_Singleton.md)
[Abstract Factory](27_Factory.md#abstract-factories).
You can easily get this effect by creating a class containing static factory methods:

```python
# facade.py
class A:
    def __init__(self, x: object) -> None: pass
class B:
    def __init__(self, x: object) -> None: pass
class C:
    def __init__(self, x: object) -> None: pass

# Other classes that aren't exposed by the
# facade go here ...

class Facade:
    @staticmethod
    def make_a(x: object) -> A:
        return A(x)

    @staticmethod
    def make_b(x: object) -> B:
        return B(x)

    @staticmethod
    def make_c(x: object) -> C:
        return C(x)

# The client programmer gets the objects
# by calling the static methods:
a = Facade.make_a(1)
b = Facade.make_b(1)
c = Facade.make_c(1.0)
```

The cleaner Python façade is a *module*.
A module already presents a curated set of names over whatever tangle of classes lives behind it,
and, as [Singleton](24_Singleton.md#a-module-is-already-a-singleton) notes,
it loads once, and every importer shares the same module.
At module level, put the friendly functions and the few classes to expose.
Keep the messy internals private (using a leading underscore, by convention),
and the `import` is the façade.
A `Facade` class full of static methods only reproduces, with more ceremony,
what a module already gives you.

This chapter completes a family of wrappers that share one structure,
a front object forwarding to something behind it,
often through the same few lines of `__getattr__()`.
What separates them is intent,
the distinction [The Pattern Concept](21_The_Pattern_Concept.md)
said remains when structures match.
A [Proxy](26_Surrogate.md#proxy)
keeps the wrapped object's interface and controls access to it.
A [Decorator](14_Decorators.md#the-decorator-pattern)
keeps the interface and layers on behavior.
An *Adapter* changes the interface into the one you need.
A *Façade* fronts a whole tangle of objects rather than one,
narrowing many interfaces down to a comfortable few.
When you cannot decide what to call your wrapper,
ask what would break if you removed it: access control, added behavior,
interface fit, or simplicity.

## Exercises

1.  Write a `PairsAdapter` that wraps a list of `(key, value)` tuples,
    following the shape of `getattr_adapter.py`.
    Give it a dictionary-style `__getitem__()` that finds a value by key,
    and forward every other attribute to the wrapped list with `__getattr__()`.
    Confirm `adapter["name"]` finds a value while `adapter.append(...)` still reaches the underlying list.
