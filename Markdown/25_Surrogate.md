# Surrogate

Both *Proxy* and *State* provide a surrogate class that you use in your code.
This surrogate class hides the real class that does the work.
When you call a method in the surrogate,
it turns around and calls the method in the implementing class.
These two patterns are so similar that the *Proxy* is a special case of *State*.

The basic idea is simple. From a base class,
you derive the surrogate along with the class or classes that provide the actual implementation:

![A surrogate and the implementation deriving from a common base class](_images/surrogate)

When you create a surrogate object, you give it an implementation.
The surrogate forwards all method calls to that implementation.

Structurally, the difference between *Proxy* and *State* is simple.
A *Proxy* has only one implementation, while *State* has more than one.
*GoF Design Patterns* considers the applications of the two patterns distinct.
*Proxy* is used to control access to its implementation,
while *State* allows you to change the implementation dynamically.
However, if you expand your notion of "controlling access to implementation," the two fit neatly together.

## Proxy

If we implement *Proxy* by following the above diagram, it looks like this:

```python
# proxy_1.py

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
#: Implementation.f()
p.g()
#: Implementation.g()
p.h()
#: Implementation.h()
```

It isn't necessary that `Implementation` have the same interface as `Proxy`.
As long as `Proxy` is somehow "speaking for" the class it forwards method calls to,
it satisfies the basic idea
(this statement is at odds with the definition for Proxy in *GoF Design Patterns*).
However, it is convenient to have a common interface that forces `Implementation` to fulfill all the methods that `Proxy` needs to call.
An abstract base class is one way to express that interface.
Each method the `Proxy` delegates to is an `@abstractmethod`,
so you cannot instantiate an implementation that omits one:

```python
# proxy_interface.py
from abc import ABC, abstractmethod

class Service(ABC):
    @abstractmethod
    def f(self) -> None: ...
    @abstractmethod
    def g(self) -> None: ...

class Complete(Service):
    def f(self) -> None: print("Complete.f()")
    def g(self) -> None: print("Complete.g()")

class Partial(Service):  # Missing g()
    def f(self) -> None: print("Partial.f()")

Complete().f()
#: Complete.f()
try:
    Partial()
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

`Complete` implements both methods and works.
`Partial` omits `g()`, so constructing it raises `TypeError` at once,
instead of failing later when the `Proxy` tries to delegate a call it cannot.

A [`Protocol`](08_Static_Typing.md#structural-typing-with-protocols) is the
structural alternative. The implementation needs no base class.
The type checker verifies conformance by shape statically,
and, with `@runtime_checkable`, `isinstance()` does so at runtime:

```python
# proxy_protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable  # Allows isinstance() against a Protocol
class Service(Protocol):
    def f(self) -> None: ...
    def g(self) -> None: ...

class Complete:          # Conforms without inheriting Service
    def f(self) -> None: print("Complete.f()")
    def g(self) -> None: print("Complete.g()")

class Partial:           # Missing g()
    def f(self) -> None: print("Partial.f()")

print(isinstance(Complete(), Service))
#: True
print(isinstance(Partial(), Service))
#: False
```

The abstract base class forces completeness at construction, through inheritance.
A `Protocol` instead reports the mismatch where code uses an object as a `Service`,
and needs no common base.
One caveat: `isinstance()` against a `@runtime_checkable` Protocol checks only
that the methods exist, not that their signatures match.
The static checker verifies signatures.

Python has a built-in delegation mechanism that makes `Proxy` even simpler to implement:

```python
# proxy_2.py
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
#: Implementation.f()
p.g()
#: Implementation.g()
p.h()
#: Implementation.h()
```

The beauty of using `__getattr__()` is that `Proxy2` is completely generic,
and not tied to any particular implementation.

## State

The *State* pattern adds more implementations to *Proxy*,
along with a way to switch from one implementation to another during the lifetime of the surrogate:

```python
# state.py
from typing import Any

class StateD:
    def __init__(self, implementation: Any) -> None:
        self.__implementation = implementation
    def change_to(self, new_implementation: Any) -> None:
        self.__implementation = new_implementation
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
#: Fiddle de dum, Fiddle de dee,
#: Eric the half a bee.
#: Ho ho ho, tee hee hee,
#: Eric the half a bee.
b.change_to(Implementation2())
run(b)
#: We're Knights of the Round Table.
#: We dance whene'er we're able.
#: We do routines and chorus scenes
#: We dance whene'er we're able.
```

The demo uses the first implementation for a while,
then swaps in the second and uses that.

Testing hands the State surrogate a small stand-in and confirms calls reach the current implementation, and that `change_to()` swaps it:

```python
# test_state.py
from state import StateD

class StateA:
    def name(self) -> str:
        return "A"

class StateB:
    def name(self) -> str:
        return "B"

def test_state_delegates_and_change_swaps() -> None:
    s = StateD(StateA())
    assert s.name() == "A"
    s.change_to(StateB())
    assert s.name() == "B"
```

The difference between *Proxy* and *State* is in the problems that are solved.
The common uses for *Proxy* as described in *GoF Design Patterns* are:

1.  *Remote proxy*.
    This proxies for an object in a different address space.
    Distributed-object systems generate these for you.
    In Python, remote procedure call (RPC) libraries play this role.
2.  *Virtual proxy*.
    This provides "lazy initialization" to create expensive objects on demand.
3.  *Protection proxy*.
    Used when you don't want the client programmer to have full access to the proxied object.
4.  *Smart reference*.
    To add actions when code accesses the proxied object.
    For example, to keep track of the number of references that are held for a particular object,
    to implement the *copy-on-write* idiom and prevent object aliasing.
    A simpler example is keeping track of the number of calls to a particular method.

A *Smart reference* proxy adds behavior around each access.
With `__getattr__()` you can wrap every method call, for example to count them:

```python
# counting_proxy.py
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
#: f()
p.g()
#: g()
p.f()
#: f()
print("calls:", p.calls)
#: calls: 3
```

Because `__getattr__()` intercepts only the lookups not found directly on the proxy,
one generic proxy can add lazy initialization (a *virtual proxy*),
access checks (a *protection proxy*),
or call tracking (a *smart reference*) to any object, with no per-method code.

*GoF Design Patterns* gives *Proxy* and *State* different structures and so treats them as unrelated.
But both are really a *Surrogate*:
a front object that passes method calls through to an implementation.
*Proxy* fronts for one implementation to control access to it.
*State* swaps among several to change behavior over time.
In Python both are the same few lines of `__getattr__()` delegation,
with *State* adding a method to change the implementation.
You need the separate implementation hierarchy that *GoF Design Patterns* uses only when you do not control the implementing code.
When you do, the single generic surrogate above is simpler and just as flexible.

Testing hands the counting proxy a small stand-in and confirms the proxy forwards the call with its result, and counts only callable accesses:

```python
# test_counting_proxy.py
from counting_proxy import CountingProxy

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
```

## Exercises

1.  Create an example of the "virtual proxy."
2.  Create an example of the "Smart reference" proxy where you keep count of the number of method calls to a particular object.
3.  Create a simple copy-on-write implementation.
