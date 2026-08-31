# Surrogate

Both *Proxy* and *State* provide a surrogate class that changes what happens behind a call without changing the calling code.
The surrogate hides the implementing class that does the work.
When you call a method in the surrogate,
the surrogate calls that method in the implementing class.
The two patterns are so similar that *Proxy* is a special case of *State*.

From a base class, derive the surrogate along with the class or classes that provide the implementation:

![Surrogate and each Implementation realize the same Interface](_images/surrogate)

This is the shape in *GoF Design Patterns*.
Python does not need the shared base,
but the base is the clearest way to see what a surrogate is.

A surrogate goes wherever an implementation goes.
A surrogate object receives an implementation and forwards all method calls to it.
Both *Proxy* and *State* use that indirection: the surrogate can refuse a call,
delay creating the implementation, count or log the calls it forwards,
or swap the implementation for another.

Structurally, *Proxy* and *State* differ in one respect.
A *Proxy* forwards to one implementation for its whole life.
*State* holds several and switches among them.

## Proxy

### Explicit Forwarding

Here the *Proxy* drops the shared base and forwards each call by hand:

```python
# proxy_1.py

class Proxy:
    def __init__(self, impl: Implementation) -> None:
        self.__implementation = impl
    # Pass method calls to the implementation:
    def f(self) -> None: self.__implementation.f()
    def g(self) -> None: self.__implementation.g()

class Implementation:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")

p = Proxy(Implementation())
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
```

### What the Implementation Supplies

`Implementation` need not have the same interface as `Proxy`.
As long as code calls `Proxy` in place of the class that `Proxy` forwards method calls to,
`Proxy` qualifies.
That is a looser definition than in *GoF Design Patterns*,
and relies only on intent.
Under GoF's stricter definition, the interface separates *Proxy* from *Adapter*.
[Telling the Wrappers Apart](29_Patterns--Changing_the_Interface.md#telling-the-wrappers-apart)
clarifies both readings.

A common interface helps, though:
`Implementation` must then supply every method that `Proxy` calls.
One way to express that interface is an abstract base class.
Each method the `Proxy` delegates to is an `@abstractmethod`,
so you cannot instantiate an implementation that omits one:

```python
# proxy_interface.py
from abc import ABC, abstractmethod
from typing import override

class Service(ABC):
    @abstractmethod
    def f(self) -> None: ...
    @abstractmethod
    def g(self) -> None: ...

class Proxy(Service):
    def __init__(self, service: Service) -> None:
        self.__service = service
    @override
    def f(self) -> None: self.__service.f()
    @override
    def g(self) -> None: self.__service.g()

class Complete(Service):
    @override
    def f(self) -> None: print("Complete.f()")
    @override
    def g(self) -> None: print("Complete.g()")

class Partial(Service):  # Missing g()
    @override
    def f(self) -> None: print("Partial.f()")

p = Proxy(Complete())
p.f()
#: Complete.f()
p.g()
#: Complete.g()
try:
    Proxy(Partial())
except TypeError as e:
    print(str(e).partition(" without")[0])
#: Can't instantiate abstract class Partial
```

Because `Proxy` accepts any `Service` and `Complete` implements both methods,
the proxy can forward either call.
Because `Partial` omits `g()`,
constructing a `Partial` raises a `TypeError` before the first call.
The inheritance makes a `Proxy` acceptable wherever code expects a `Service`,
and the type checker verifies the `Proxy`'s `f()` and `g()` against the base.

A [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
is the structural alternative: the implementation needs no base class.
The type checker verifies the shape statically,
and `@runtime_checkable` lets `isinstance()` check the shape at runtime:

```python
# proxy_protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable  # Allows isinstance() on a Protocol
class Service(Protocol):
    def f(self) -> None: ...
    def g(self) -> None: ...

class Complete:  # Conforms without inheriting Service
    def f(self) -> None: print("Complete.f()")
    def g(self) -> None: print("Complete.g()")

class Partial:  # Missing g()
    def f(self) -> None: print("Partial.f()")

print(isinstance(Complete(), Service))
#: True
print(isinstance(Partial(), Service))
#: False
```

With inheritance, the abstract base class rejects an incomplete implementation at construction.
A `Protocol` instead reports the mismatch where code uses an object as a `Service`,
and needs no common base.
One caveat: `isinstance()` against a `@runtime_checkable` Protocol checks only that the methods exist,
not that their signatures match.
The static type checker verifies signatures.

### Forwarding with `__getattr__()` {#forwarding-with-getattr}

Python's built-in delegation mechanism, `__getattr__()`,
which [Singleton](24_Patterns--Singleton.md) used to reach its inner object,
makes `Proxy` simpler to implement:

```python
# proxy_2.py
from typing import Any

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Implementation:
    def f(self) -> None:
        print("Implementation.f()")
    def g(self) -> None:
        print("Implementation.g()")
    def h(self) -> None:  # New; Proxy needs no change
        print("Implementation.h()")

p = Proxy(Implementation())
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
p.h()
#: Implementation.h()
```

`__getattr__()` makes the forwarding generic:
because `Proxy` names no methods in `Implementation`,
it keeps working when you add a method to the implementation.
`Implementation` here has an `h()` that `proxy_1.py`'s lacked,
and `p.h()` forwards it without changing `Proxy`.

The double underscore on `self.__implementation` matters:
the name [mangles](11_Techniques--Testing.md#white-box-and-black-box-tests)
to `_Proxy__implementation`,
so it cannot collide with an attribute the implementation defines.

Do not confuse `__getattr__()` with its lookalike, `__getattribute__()`.
`__getattr__()` is the *fallback* hook:
Python calls it only after normal lookup fails.
Normal lookup finds `self.__implementation`,
so reading that name in the hook's body does not call the hook again.
`__getattribute__()` intercepts every attribute access,
including each `self.` access in its own body,
so the naive version calls itself forever.
Writing a `__getattribute__()` means calling `object.__getattribute__()` for every internal access,
machinery a surrogate rarely needs.

The abstract base class in `proxy_interface.py` and the `Protocol` in `proxy_protocol.py` still guard the implementation side:
the type checker verifies that whatever you provide to the proxy has the necessary methods.
Calls on the proxy get no such check.
Because `__getattr__()` resolves `p.f()` and returns `Any`,
the checker cannot verify that call.
With explicit forwarding, as in `proxy_1.py`,
`p.f()` reaches a declared method with a declared return type,
and the checker verifies the call.
`proxy_interface.py`'s `Proxy` also passes as a `Service`:
because it inherits `Service`, code typed against `Service` accepts it.
`__getattr__()` gives up that check so it can forward every method,
including ones added later.

The lost static check is the first of four limits on `__getattr__()` delegation.
The next three sections cover the rest:
Python never calls `__getattr__()` for a special-method lookup or for an assignment,
and `__getattr__()` calls itself when the name it reads is also missing.

### Special Methods Bypass `__getattr__()` {#special-methods-bypass-getattr}

Python looks up dunders like `__len__()` and `__str__()` on the proxy's type,
not on the implementation, so `len(p)` and `print(p)` do not delegate,
even though an explicit `p.__len__()` does:

```python
# dunder_bypass.py
from typing import Any

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

p = Proxy(Words())
print(p.__len__())  # The explicit call delegates
#: 2
try:
    # Special-method lookup skips the instance:
    len(p)  # type: ignore
except TypeError as e:
    print(e)
#: object of type 'Proxy' has no len()
print("__main__.Proxy object" in str(p))
#: True
```

The two calls look interchangeable and are not.
`p.__len__()` is ordinary attribute access,
so the failed instance lookup falls through to `__getattr__()`, which delegates.
`len(p)` looks up `__len__()` on `type(p)`, skips the instance, finds none,
and reports that `Proxy` has no `len()`.
The type checker rejects `len(p)` statically for the same reason,
so the listing needs the `# type: ignore` to show the runtime failure.
A proxy that must forward special methods defines them explicitly.

`len(p)` reports the missing method because `object` defines no `__len__()`.
`print(p)` cannot: `object` defines `__str__()`,
so the lookup on `type(p)` finds `object`'s `__str__()` and the proxy prints as itself.
Whenever `object` defines the dunder, the bypass raises no error.
The proxy answers with `object`'s version,
and the call never reaches the implementation.

### Forwarding Writes

Delegation using `__getattr__()` forwards reads but not writes:

```python
# proxy_writes.py
from typing import Any

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Settings:
    def __init__(self) -> None:
        self.level = "low"

settings = Settings()
p = Proxy(settings)
print(p.level)
#: low
p.level = "high"  # type: ignore
print(p.level, settings.level)
#: high low
```

`__getattr__()` is a read hook: Python calls it for a failed read,
never for an assignment.
The assignment stores `level` in the proxy's `__dict__`,
not the implementation's `__dict__`.
The next `p.level` lookup succeeds without calling `__getattr__()`.
The proxy reports `"high"` and the implementation reports `"low"`.
The type checker rejects the assignment because `Proxy` declares no `level` and no `__setattr__()` that would accept one.

To forward writes, define `__setattr__()`.
`__setattr__()` then intercepts every assignment,
including the one in `__init__()`.
Forwarding that first assignment would recurse,
because the implementation does not exist yet,
so `__init__()` stores the implementation another way:

```python
# proxy_setattr.py
from typing import Any

class WriteProxy:
    def __init__(self, impl: Any) -> None:
        object.__setattr__(self, "_implementation", impl)
    def __getattr__(self, name: str) -> Any:
        return getattr(self._implementation, name)
    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._implementation, name, value)

class Settings:
    def __init__(self) -> None:
        self.level = "low"

settings = Settings()
p = WriteProxy(settings)
p.level = "high"
print(p.level, settings.level)
#: high high
```

`object.__setattr__()` stores `_implementation` on the proxy without going through `__setattr__()`.
Now every assignment after `__init__()` reaches the implementation via the new `__setattr__()`,
so the proxy and the implementation report the same value.
`WriteProxy` needs no `# type: ignore`,
because a declared `__setattr__()` makes the type checker accept assignment to any attribute name.

The implementation attribute no longer needs a double underscore.
Mangling rewrites identifiers, not string literals,
so storing a double-underscore name through `object.__setattr__()` would mean writing the mangled form,
`"_WriteProxy__implementation"`, by hand.

### The Recursion Trap

The fallback hook `__getattr__()` can recurse.
If `__getattr__()`'s body reads a proxy attribute that does not exist,
the failed lookup calls `__getattr__()` again.
Python reports this as a `RecursionError`,
not the `AttributeError` that would name the cause.

A misspelled `self._implementation` is one cause.
Rebuilding a proxy through `copy.copy()` or `pickle` is another:
both construct the new instance without calling `__init__()`,
so no `_implementation` exists when the first failed lookup calls `__getattr__()`.
The fix is a guard at the top of `__getattr__()` that raises `AttributeError` for any name that starts with an underscore:

```python
# getattr_guard.py
from typing import Any

class Proxy:
    def __init__(self, impl: Any) -> None:
        self._implementation = impl
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):  # The guard
            raise AttributeError(name)
        return getattr(self._imp, name)  # Deliberate typo

class Implementation:
    def f(self) -> None: print("Implementation.f()")

try:
    Proxy(Implementation()).f()
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError _imp
```

Without the guard, the misspelled `self._imp` produces a `RecursionError` that names nothing.
With the guard, the second call to `__getattr__()` reports the typo by name.
The guard also makes the proxy work with `copy` and `pickle`,
which look up `__setstate__()` before `__init__()` has run.
Both get an `AttributeError`, which those modules handle, instead of recursing.

This chapter's other `__getattr__()` proxies do not include the guard.
This way, each listing shows one idea.

### A Surrogate Is Not Its Implementation

A proxy is not an instance of the implementation's class.
Delegation forwards the methods, not the type,
and `isinstance()` checks only the proxy's own class.
A `@runtime_checkable` `Protocol` does not change that.
Since Python 3.12 the Protocol check uses `inspect.getattr_static()`,
which reads the class and instance dictionaries instead of running attribute lookup.
That function never calls `__getattr__()`,
so a proxy that supplies every method through `__getattr__()` also fails the `isinstance()` check.
Because ordinary attribute access still finds those methods,
`hasattr(p, "f")` is `True` and `p.f()` runs.
Code that calls the method, or checks with `hasattr()`, works on a surrogate.

```python
# proxy_identity.py
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class Service(Protocol):
    def f(self) -> None: ...

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Implementation:
    def f(self) -> None: print("Implementation.f()")

p = Proxy(Implementation())
p.f()
#: Implementation.f()
print(hasattr(p, "f"))
#: True
print(isinstance(p, Implementation), isinstance(p, Service))
#: False False
```

The call works and `hasattr()` finds the method,
yet both `isinstance()` checks return `False`.

Two workarounds make `isinstance()` return `True`,
and neither verifies anything:

-   `Service.register(Proxy)` tells the ABC machinery to answer `True` for every `Proxy`,
    without looking at its methods.
-   A `__class__` property returning the implementation's class makes `isinstance()` see that class rather than `Proxy`.

Both satisfy the runtime check and neither satisfies a type checker.
Inheritance satisfies both.
`proxy_interface.py`'s `Proxy` inherits `Service`,
so `isinstance(p, Service)` returns `True`,
and the type checker confirms that `Proxy`'s `f()` and `g()` match `Service`.
Forwarding through `__getattr__()` gives up both.
A surrogate is not its implementation,
and code that checks with `isinstance()` should check for the method instead.

### What Proxy Solves

*GoF Design Patterns* lists these common uses for *Proxy*:

1.  *Remote proxy*.
    Proxies for an object in a different address space.
    Distributed-object systems generate these.
    In Python, remote procedure call (RPC) libraries provide them.
2.  *Virtual proxy*.
    Provides "lazy initialization" to create expensive objects on demand.
3.  *Protection proxy*.
    Restricts the client programmer's access to the proxied object.
4.  *Smart reference*.
    Adds actions when code accesses the proxied object.
    For example, a smart reference can the calls to a particular method.
    It can also count the references to an object,
    implementing the *copy-on-write* idiom and preventing aliasing.

A *Protection proxy* decides whether a call reaches the implementation.
Because `__getattr__()` receives the requested name, the check is one condition:

```python
# protection_proxy.py
from typing import Any, Final

READ_ONLY: Final[frozenset[str]] = frozenset({"read"})

class Guarded:
    def __init__(self, doc: Document, *,
                 admin: bool) -> None:
        self._doc = doc
        self._admin = admin
    def __getattr__(self, name: str) -> Any:
        if not self._admin and name not in READ_ONLY:
            raise PermissionError(name)
        return getattr(self._doc, name)

class Document:
    def read(self) -> str: return "contents"
    def erase(self) -> None: print("erased")

guest = Guarded(Document(), admin=False)
print(guest.read())
#: contents
try:
    guest.erase()
except PermissionError as e:
    print(type(e).__name__, e)
#: PermissionError erase
Guarded(Document(), admin=True).erase()
#: erased
```

That refusal separates a *Proxy* from a *Decorator*:
a decorator adds behavior around a call it always makes.
This proxy decides whether to forward the call.

A *Smart reference* proxy adds behavior around each access without refusing any.
With `__getattr__()` you can wrap every method call, for example to count them.
This proxy names its implementation `_impl`, with one underscore,
and so gives up the mangling that kept `proxy_2.py`'s attribute from colliding.
`_impl` and `calls` now share a namespace with the implementation's own attributes:
read `calls` from the proxy and you get the counter,
even when the implementation defines a `calls` of its own.

```python
# counting_proxy.py
from typing import Any

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

class Implementation:
    def f(self) -> None: print("f()")
    def g(self) -> None: print("g()")

if __name__ == "__main__":
    p = CountingProxy(Implementation())
    p.f()
    p.g()
    p.f()
    print("calls:", p.calls)
#: f()
#: g()
#: f()
#: calls: 3
```

Python calls `__getattr__()` for any name the proxy and its class lack,
and never for the proxy's own attributes.
The proxy therefore names no method of the implementation while still keeping state of its own.
The same few lines serve lazy initialization (a *virtual proxy*), access checks
(a *protection proxy*), or call tracking (a *smart reference*), over any object.

The counting proxy's test confirms that a call reaches the implementation and returns its result,
and that the proxy counts calls without counting an attribute read:

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
    # Non-callable attribute passes through
    assert p.answer == 42
    p2 = CountingProxy(Doubler())
    p2.double(1)
    p2.double(1)
    assert p.calls == 0
    assert p2.calls == 2
```

## State

The *State* pattern adds more implementations to *Proxy*,
along with a way to switch implementations during the surrogate's lifetime:

```python
# state_surrogate.py
from typing import Any, Protocol

class Behavior(Protocol):
    def f(self) -> None: ...
    def g(self) -> None: ...
    def h(self) -> None: ...

class Surrogate:
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

if __name__ == "__main__":
    first: Behavior = Implementation1()
    second: Behavior = Implementation2()
    b = Surrogate(first)
    run(b)
    b.change_to(second)
    run(b)
#: Fiddle de dum, Fiddle de dee,
#: Eric the half a bee.
#: Ho ho ho, tee hee hee,
#: Eric the half a bee.
#: We're Knights of the Round Table.
#: We dance whene'er we're able.
#: We do routines and chorus scenes
#: We dance whene'er we're able.
```

`run()` never changes and neither does `b`.
Only the implementation the surrogate forwards to does.
Here the client programmer calls `change_to()`.
[State Machines](31_Patterns--State_Machines.md)
makes each implementation choose its own successor,
so the surrogate advances without the client asking.

The annotations that carry the implementation are all `Any`,
which the book's typing guidance treats as a last resort,
and the two uses have different reasons.

`run(b: Any)` has no alternative.
Annotating `run(b: Behavior)` and passing it `b` is a type error,
because `Surrogate` defines no `f()` of its own, and,
as [Forwarding with `__getattr__()`](#forwarding-with-getattr) explains,
the checker cannot verify a method that `__getattr__()` supplies.

`Surrogate.__init__()` and `change_to()` are a choice.
Annotating both parameters `Behavior` type-checks,
and the checker then verifies every implementation that reaches either method.
That annotation also ties the surrogate to one Protocol,
and that tie is what the generic surrogate exists to avoid:
`test_state.py` below passes the same `Surrogate` a two-state stand-in that has a `name()` and none of `Behavior`'s three methods.
Declaring the implementations instead,
as `first: Behavior` and `second: Behavior` do,
puts the check where it does not restrict the surrogate:
the type checker verifies that `Implementation1` and `Implementation2` supply everything the Protocol declares,
and reports a missing method.
That declaration covers the implementations, not the surrogate.

The test passes the State surrogate a small stand-in and confirms that calls reach the current implementation and that `change_to()` swaps it:

```python
# test_state.py
from state_surrogate import Surrogate

class StateA:
    def name(self) -> str:
        return "A"

class StateB:
    def name(self) -> str:
        return "B"

def test_state_delegates_and_change_swaps() -> None:
    s = Surrogate(StateA())
    assert s.name() == "A"
    s.change_to(StateB())
    assert s.name() == "B"
```

## One Surrogate, Two Intents

Because *GoF Design Patterns* gives *Proxy* and *State* different structures,
it treats them as unrelated.
But both are a *Surrogate*:
an object that forwards method calls to an implementation.
*Proxy* forwards to one implementation to control access to it.
*State* swaps among several to change behavior over time.
In Python both are the same few lines of `__getattr__()` delegation,
with *State* adding a method to change the implementation.
The separate implementation hierarchy in *GoF Design Patterns* matters when other people write the implementations and you need the base class to state which methods an implementation must supply.
When you write both sides,
the single generic surrogate in `state_surrogate.py` is simpler and just as flexible.

## Exercises

1.  Create an example of the "virtual proxy."
2.  Change `CountingProxy` in `counting_proxy.py` to keep a per-method tally in a `collections.Counter` instead of a single total.
    Confirm the tally reports `f` called twice and `g` called once.
3.  Create a simple copy-on-write implementation.
4.  In `counting_proxy.py`,
    misspell `self._impl` as `self._imp` inside `__getattr__()` and run it.
    Use the fallback-hook behavior this chapter describes to explain why the failure reports as `RecursionError` rather than an `AttributeError` naming the typo.
5.  Create a program similar to a DBMS that allows only a fixed number of connections at a time.
    Implement this with a singleton-like system
    ([Singleton](24_Patterns--Singleton.md))
    that controls the number of "connection" objects it creates.
    When a user finishes with a connection,
    the system must check that connection back in for reuse.
    To guarantee this, return a proxy instead of a reference to the actual connection,
    and design the proxy to release the connection back to the system.
6.  `dunder_bypass.py`'s `Proxy` cannot answer `len(p)`.
    Give that `Proxy` a `__len__()` that forwards to the implementation,
    and confirm `len(p)` returns 2.
    Then explain why `__getattr__()` could not have supplied it.
7.  Extend `Surrogate` in `state_surrogate.py` so `change_to()` rejects an implementation missing a method the current one has,
    and explain why the type checker could not have reported that swap.
