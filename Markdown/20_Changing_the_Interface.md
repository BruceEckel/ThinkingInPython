# Changing the Interface

Sometimes the problem that you're solving is as simple as "I don't have
the interface that I want." Two of the patterns in *Design Patterns*
solve this problem: *Adapter* takes one type and produces an interface
to some other type. *Façade* creates an interface to a set of classes,
simply to provide a more comfortable way to deal with a library or
bundle of resources.

## Adapter

When you've got *this*, and you need *that*, *Adapter* solves the
problem. The only requirement is to produce a *that*, and there are a
number of ways you can accomplish this adaptation:

```python
# ChangeInterface/Adapter.py
# Variations on the Adapter pattern.

class WhatIHave:
    def g(self): pass
    def h(self): pass

class WhatIWant:
    def f(self): pass

class ProxyAdapter(WhatIWant):
    def __init__(self, whatIHave):
        self.whatIHave = whatIHave

    def f(self):
        # Implement behavior using
        # methods in WhatIHave:
        self.whatIHave.g()
        self.whatIHave.h()

class WhatIUse:
    def op(self, whatIWant):
        whatIWant.f()

# Approach 2: build adapter use into op():
class WhatIUse2(WhatIUse):
    def op(self, whatIHave):
        ProxyAdapter(whatIHave).f()

# Approach 3: build adapter into WhatIHave:
class WhatIHave2(WhatIHave, WhatIWant):
    def f(self):
        self.g()
        self.h()

# Approach 4: use an inner class:
class WhatIHave3(WhatIHave):
    class InnerAdapter(WhatIWant):
        def __init__(self, outer):
            self.outer = outer
        def f(self):
            self.outer.g()
            self.outer.h()

    def whatIWant(self):
        return WhatIHave3.InnerAdapter(self)

whatIUse = WhatIUse()
whatIHave = WhatIHave()
adapt= ProxyAdapter(whatIHave)
whatIUse2 = WhatIUse2()
whatIHave2 = WhatIHave2()
whatIHave3 = WhatIHave3()
whatIUse.op(adapt)
# Approach 2:
whatIUse2.op(whatIHave)
# Approach 3:
whatIUse.op(whatIHave2)
# Approach 4:
whatIUse.op(whatIHave3.whatIWant())
```

I'm taking liberties with the term "proxy" here, because in *Design
Patterns* they assert that a proxy must have an identical interface with
the object that it is a surrogate for. However, if you have the two
words together: "proxy adapter," it is perhaps more reasonable.

### Adapter in Python

The four variations above are Java habits. Python is duck-typed: `WhatIUse.op()`
only calls `f()`, so it accepts *any* object that has an `f()`. You do not need a
shared base class or a declared interface, only the method. The common adapter
need is "forward most calls unchanged, and add or change a few." `__getattr__`
does the forwarding, so the adapter stays tiny:

```python
# ChangeInterface/getattr_adapter.py
# The usual adapter need: forward most calls, change a few. __getattr__
# delegates everything you do not override, so the wrapper stays small.
from typing import Any


class WhatIHave:
    def g(self) -> str: return "g"
    def h(self) -> str: return "h"


class Adapter:
    def __init__(self, adaptee: WhatIHave) -> None:
        self._adaptee = adaptee

    def f(self) -> str:                       # the new interface
        return self._adaptee.g() + self._adaptee.h()

    def __getattr__(self, name: str) -> Any:  # forward everything else
        return getattr(self._adaptee, name)


a = Adapter(WhatIHave())
print(a.f())   # adapted method
print(a.g())   # forwarded to the adaptee unchanged
```

`__getattr__` runs only for attributes Python does not find normally, so `f()`
uses the adapter's own version while everything else falls through to the
adaptee. This is the idiomatic Python adapter: a thin wrapper, not a hierarchy.

## Façade

A general principle that I apply when I'm casting about trying to mold
requirements into a first-cut object is "If something is ugly, hide it
inside an object." This is basically what *Façade* accomplishes. If you
have a rather confusing collection of classes and interactions that the
client programmer doesn't really need to see, then you can create an
interface that is useful for the client programmer and that only
presents what's necessary.

Façade is often implemented as singleton abstract factory. Of course,
you can easily get this effect by creating a class containing `static`
factory methods:

```python
# ChangeInterface/Facade.py
class A:
    def __init__(self, x): pass
class B:
    def __init__(self, x): pass
class C:
    def __init__(self, x): pass

# Other classes that aren't exposed by the
# facade go here ...

class Facade:
    def makeA(x): return A(x)
    makeA = staticmethod(makeA)
    def makeB(x): return B(x)
    makeB = staticmethod(makeB)
    def makeC(x): return C(x)
    makeC = staticmethod(makeC)

# The client programmer gets the objects
# by calling the static methods:
a = Facade.makeA(1);
b = Facade.makeB(1);
c = Facade.makeC(1.0);
```

The cleaner Python façade is a *module*. A module already presents a curated set
of names over whatever tangle of classes lives behind it, and, as [the Singleton chapter](13_The_Singleton.md)
notes, it is imported once and shared everywhere. Put the friendly
functions and the few classes you want to expose at module level, keep the messy
internals private (a leading underscore, by convention), and the `import` *is*
the façade. A `Facade` class full of static methods only reproduces, with more
ceremony, what a module gives you for free.

## Exercises

1.  Create an adapter class that automatically loads a two-dimensional
    array of objects into a dictionary as key-value pairs.
