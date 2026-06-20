# Fronting for an Implementation

Both *Proxy* and *State* provide a surrogate class that you use in your code;
the real class that does the work is hidden behind this surrogate class.
When you call a method in the surrogate,
it turns around and calls the method in the implementing class.
These two patterns are so similar that the *Proxy* is a special case of *State*.

The basic idea is simple: from a base class,
the surrogate is derived along with the class or classes that provide the actual implementation:

![A surrogate and the implementation deriving from a common base class](_images/surrogate)

When a surrogate object is created,
it is given an implementation to which to send all of the method calls.

Structurally, the difference between *Proxy* and *State* is simple:
a *Proxy* has only one implementation, while *State* has more than one.
The application of the patterns is considered (in *Design Patterns*) to be distinct:
*Proxy* is used to control access to its implementation,
while *State* allows you to change the implementation dynamically.
However, if you expand your notion of "controlling access to implementation" then the two fit neatly together.

## Proxy

If we implement *Proxy* by following the above diagram, it looks like this:

```python
# proxy_demo.py
# Simple demonstration of the Proxy pattern.

class Implementation:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")
    def h(self) -> None:
        print("Implementation.h()")

class Proxy:
    def __init__(self) -> None:
        self.__implementation = Implementation()
    # Pass method calls to the implementation:
    def f(self) -> None: self.__implementation.f()
    def g(self) -> None: self.__implementation.g()
    def h(self) -> None: self.__implementation.h()

p = Proxy()
p.f()
p.g()
p.h()
```

It isn't necessary that `Implementation` have the same interface as `Proxy`;
as long as `Proxy` is somehow "speaking for" the class that it is referring method calls to then the basic idea is satisfied (note that this statement is at odds with the definition for Proxy in GoF).
However, it is convenient to have a common interface so that `Implementation` is forced to fulfill all the methods that `Proxy` needs to call.

Python has a built-in delegation mechanism that makes `Proxy` even simpler to implement:

```python
# proxy_demo2.py
# Simple demonstration of the Proxy pattern.
from typing import Any


class Implementation2:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")
    def h(self) -> None:
        print("Implementation.h()")

class Proxy2:
    def __init__(self) -> None:
        self.__implementation = Implementation2()
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy2()
p.f()
p.g()
p.h()
```

The beauty of using `__getattr__()` is that `Proxy2` is completely generic,
and not tied to any particular implementation.

## State

The *State* pattern adds more implementations to *Proxy*,
along with a way to switch from one implementation to another during the lifetime of the surrogate:

```python
# state_demo.py
# Simple demonstration of the State pattern.
from typing import Any


class StateD:
    def __init__(self, imp: Any) -> None:
        self.__implementation = imp
    def change_imp(self, new_imp: Any) -> None:
        self.__implementation = new_imp
    # Delegate calls to the implementation:
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Implementation1:
    def f(self) -> None:
        print("Fiddle de dum, Fiddle de dee,")
    def g(self) -> None:
        print("Eric the half a bee.")
    def h(self) -> None:
        print("Ho ho ho, tee hee hee,")

class Implementation2:
    def f(self) -> None:
        print("We're Knights of the Round Table.")
    def g(self) -> None:
        print("We dance whene'er we're able.")
    def h(self) -> None:
        print("We do routines and chorus scenes")

def run(b: Any) -> None:
    b.f()
    b.g()
    b.h()
    b.g()

b = StateD(Implementation1())
run(b)
b.change_imp(Implementation2())
run(b)
```

You can see that the first implementation is used for a bit,
then the second implementation is swapped in and that is used.

The difference between *Proxy* and *State* is in the problems that are solved.
The common uses for *Proxy* as described in *Design Patterns* are:

1.  `Remote proxy`.
    This proxies for an object in a different address space.
    A remote proxy is created for you automatically by the RMI compiler `rmic` as it creates stubs and skeletons.
2.  `Virtual proxy`.
    This provides "lazy initialization" to create expensive objects on demand.
3.  `Protection proxy`.
    Used when you don't want the client programmer to have full access to the proxied object.
4.  `Smart reference`.
    To add additional actions when the proxied object is accessed.
    For example, to keep track of the number of references that are held for a particular object,
    in order to implement the *copy-on-write* idiom and prevent object aliasing.
    A simpler example is keeping track of the number of calls to a particular method.

A *Smart reference* proxy adds behavior around each access.
With `__getattr__` you can wrap every method call, for example to count them:

```python
# counting_proxy.py
# A "smart reference" proxy: count calls by intercepting attribute
# access.
from typing import Any


class Implementation:
    def f(self) -> None: print("f()")
    def g(self) -> None: print("g()")


class CountingProxy:
    def __init__(self, impl: Any) -> None:
        self._impl = impl
        self.calls = 0

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._impl, name)
        if callable(attr):
            def counted(*args: Any, **kwargs: Any) -> Any:
                self.calls += 1
                return attr(*args, **kwargs)
            return counted
        return attr


p = CountingProxy(Implementation())
p.f()
p.g()
p.f()
print("calls:", p.calls)
```

Because `__getattr__` intercepts only the lookups not found directly on the proxy,
one generic proxy can add lazy initialization (a *virtual proxy*),
access checks (a *protection proxy*),
or call tracking (a *smart reference*) to any object, with no per-method code.

In *Design Patterns*,
*Proxy* and *State* are given different structures and so are treated as unrelated.
But both are really a *Surrogate*:
a front object that passes method calls through to an implementation.
*Proxy* fronts for one implementation to control access to it;
*State* swaps among several to change behavior over time.
In Python both are the same few lines of `__getattr__` delegation,
with *State* adding a method to change the implementation.
The separate implementation hierarchy that *Design Patterns* uses is needed only when you do not control the implementing code;
when you do, the single generic surrogate above is simpler and just as flexible.

## Testing the Surrogates

Because each surrogate wraps any object,
a test can hand it a small stand-in with real return values and check the delegation directly.
For the proxy, that the call is forwarded with its result and counted;
for the state, that calls reach the current implementation and that `change_imp` swaps it:

```python
# test_fronting.py
from counting_proxy import CountingProxy
from state_demo import StateD


class Doubler:
    def double(self, n: int) -> int:
        return n * 2


def test_proxy_forwards_call_and_result() -> None:
    p = CountingProxy(Doubler())
    assert p.double(5) == 10
    assert p.double(3) == 6


def test_proxy_counts_only_calls() -> None:
    class HasValue:
        answer = 42

    p = CountingProxy(HasValue())
    assert p.answer == 42  # Non-callable attribute passes through
    p2 = CountingProxy(Doubler())
    p2.double(1)
    p2.double(1)
    assert p.calls == 0
    assert p2.calls == 2


class StateA:
    def name(self) -> str:
        return "A"


class StateB:
    def name(self) -> str:
        return "B"


def test_state_delegates_and_change_imp_swaps() -> None:
    s = StateD(StateA())
    assert s.name() == "A"
    s.change_imp(StateB())
    assert s.name() == "B"
```
