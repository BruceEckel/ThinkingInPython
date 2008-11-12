
********************************************************************************
Changing the Interface
********************************************************************************

Sometimes the problem that you're solving is as simple as "I don't have the
interface that I want." Two of the patterns in *Design Patterns* solve this
problem: *Adapter* takes one type and produces an interface to some other type.
*Façade* creates an interface to a set of classes, simply to provide a more
comfortable way to deal with a library or bundle of resources.

Adapter
=======================================================================

When you've got *this*, and you need *that*, *Adapter* solves the problem. The
only requirement is to produce a *that*, and there are a number of ways you can
accomplish this adaptation::

    # changeInterface/Adapter.py
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

I'm taking liberties with the term "proxy" here, because in *Design Patterns*
they assert that a proxy must have an identical interface with the object that
it is a surrogate for. However, if you have the two words together: "proxy
adapter," it is perhaps more reasonable.

Façade
=======================================================================

A general principle that I apply when I'm casting about trying to mold
requirements into a first-cut object is "If something is ugly, hide it inside an
object." This is basically what *Façade* accomplishes. If you have a rather
confusing collection of classes and interactions that the client programmer
doesn't really need to see, then you can create an interface that is useful for
the client programmer and that only presents what's necessary.

Façade is often implemented as singleton abstract factory. Of course, you can
easily get this effect by creating a class containing **static** factory
methods::

    # changeInterface/Facade.py
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

[rewrite this section using research from Larman's book]

Example for Facade (?): my "nicer" version of the XML library.

Exercises
=======================================================================

#.  Create an adapter class that automatically loads a two-dimensional array of
    objects into a dictionary as key-value pairs.



