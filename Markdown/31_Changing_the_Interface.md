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
    def g(self) -> None: ...
    def h(self) -> None: ...

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
what_i_use.op(adapt)
# Approach 2:
what_i_use2.op(what_i_have)
# Approach 3:
what_i_use.op(what_i_have2)
# Approach 4:
what_i_use.op(what_i_have3.what_i_want())
```

This takes liberty with the term "[Proxy](26_Surrogate.md#proxy),"
because *GoF Design Patterns* asserts that a Proxy must have an identical interface with the object for which it is a surrogate.

### Adapter in Python

The four variations above are Java habits.
Python is dynamically typed. `WhatIUse.op()` only calls `f()`,
so it accepts any object that has an `f()`.
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

    def f(self) -> str:                       # The new interface
        return self._adaptee.g() + self._adaptee.h()

    def __getattr__(self, name: str) -> Any:  # Forwards the rest
        return getattr(self._adaptee, name)

a = Adapter(WhatIHave())
print(a.f())   # Adapted method
#: gh
print(a.g())   # Forwarded to the adaptee unchanged
#: g
```

`__getattr__()` runs only for attributes Python does not find normally,
so `f()` uses the adapter's own version while everything else falls through to the adaptee.
This is the idiomatic Python adapter: a thin wrapper, not a hierarchy.

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

A Façade often takes the form of a [Singleton](24_Singleton.md) [Abstract Factory](29_Factory.md#abstract-factories).
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
what a module gives you for free.

## Exercises

1.  Create an adapter class that automatically loads a two-dimensional array of objects into a dictionary as key-value pairs.
