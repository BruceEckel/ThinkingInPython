# Surrogate

Both *Proxy* and *State* provide a surrogate class that you use in your code.
This surrogate class hides the real class that does the work.
When you call a method in the surrogate,
it turns around and calls the method in the implementing class.
These two patterns are so similar that the *Proxy* is a special case of *State*.

From a base class, you derive the surrogate along with the class or classes that provide the actual implementation:

![A surrogate and the implementation deriving from a common base class](_images/surrogate)

That is the shape *GoF Design Patterns* draws.
Python does not need the shared base, as the listings below show,
but it is the clearest way to see what a surrogate is.

A surrogate object acquires an implementation,
either constructing one or receiving one.
The surrogate forwards all method calls to that implementation.

Structurally, *Proxy* and *State* differ in one respect.
A *Proxy* has only one implementation, while *State* has more than one.
*GoF Design Patterns* considers the applications of the two patterns distinct.
*Proxy* controls access to its implementation,
while *State* lets you change the implementation dynamically.
However, if you expand your notion of "controlling access to implementation,"
the two fit neatly together.

## Proxy

If you implement *Proxy* by following the above diagram, it looks like this:

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
As long as `Proxy` is somehow "speaking for" the class to which it forwards method calls,
it satisfies the basic idea.
That is a looser definition than *GoF Design Patterns* uses.
Under GoF's stricter definition the interface separates *Proxy* from *Adapter*;
under the looser one used here it is the intent.
[Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart)
sorts out both readings.

However, it is convenient to have a common interface that forces `Implementation` to fulfill all the methods that `Proxy` needs to call.
An abstract base class is one way to express that interface.
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

class Complete(Service):
    @override
    def f(self) -> None: print("Complete.f()")
    @override
    def g(self) -> None: print("Complete.g()")

class Partial(Service):  # Missing g()
    @override
    def f(self) -> None: print("Partial.f()")

class Proxy:
    def __init__(self, service: Service) -> None:
        self.__service = service
    def f(self) -> None: self.__service.f()
    def g(self) -> None: self.__service.g()

p = Proxy(Complete())
p.f()
#: Complete.f()
p.g()
#: Complete.g()
try:
    Partial()
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

`Proxy` accepts any `Service`, and `Complete` implements both methods,
so the proxy can forward either call.
`Partial` omits `g()`, so constructing it raises `TypeError` at once,
instead of failing later,
when the `Proxy` delegates a call the implementation cannot answer.

A [`Protocol`](08_Static_Typing.md#structural-typing-with-protocols)
is the structural alternative.
The implementation needs no base class.
The type checker verifies conformance by shape statically, and,
with `@runtime_checkable`, `isinstance()` does so at runtime:

```python
# proxy_protocol.py
from typing import Protocol, runtime_checkable

@runtime_checkable  # Allows isinstance() against a Protocol
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

The abstract base class forces completeness at construction,
through inheritance.
A `Protocol` instead reports the mismatch where code uses an object as a `Service`,
and needs no common base.
One caveat: `isinstance()` against a `@runtime_checkable` Protocol checks only that the methods exist,
not that their signatures match.
The static checker verifies signatures.

Python has a built-in delegation mechanism, `__getattr__()`,
that makes `Proxy` even simpler to implement:

```python
# proxy_2.py
from typing import Any

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
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy()
p.f()
#: Implementation.f()
p.g()
#: Implementation.g()
p.h()
#: Implementation.h()
```

`__getattr__()` makes the forwarding generic:
`Proxy` names no method of `Implementation`,
so it keeps working when the implementation grows a method.
The proxy is still tied to one implementation class, which it constructs itself;
accepting an implementation as a constructor argument removes that tie too.
The double underscore on `self.__implementation` matters:
the name [mangles](11_Testing.md#white-box-and-black-box-tests)
to `_Proxy__implementation`,
so it cannot collide with an attribute the implementation carries.

Do not confuse `__getattr__()` with its lookalike, `__getattribute__()`.
The one used here is the *fallback* hook:
Python calls it only after normal lookup fails,
which is why `self.__implementation` inside it resolves normally.
`__getattribute__()` intercepts every attribute access,
including each `self.` access in its own body,
so the naive version calls itself forever.
Writing one means routing every internal access through `object.__getattribute__()`,
machinery a surrogate rarely needs.

The interface work above still applies on the implementation side:
the checker verifies that whatever you hand the proxy has the methods.
That verification stops at the proxy.
`p.f()` goes through `__getattr__()`, whose return type is unknown,
so nothing the proxy declares can make that call checkable.
Explicit forwarding, as in `proxy_1.py`,
is the version a checker can see through; `__getattr__()` trades that for reach.

One limit: special methods bypass `__getattr__()`.
Python looks up dunders like `__len__()` and `__str__()` on the proxy's type,
not on the instance, so `len(p)` and `print(p)` do not delegate,
even though an explicit `p.__len__()` would:

```python
# dunder_bypass.py
from typing import Any

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

class Proxy:
    def __init__(self) -> None:
        self.__implementation = Words()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy()
print(p.__len__())  # The explicit call delegates
#: 2
try:
    # Special-method lookup skips the instance:
    len(p)  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
print("Proxy object at" in str(p))
#: True
```

The two calls look interchangeable and are not.
`p.__len__()` is ordinary attribute access,
so the failed instance lookup falls through to `__getattr__()`, which delegates.
`len(p)` asks `type(p)` for `__len__()` directly, finds none,
and reports that `Proxy` has no length.
The type checker agrees, rejecting `len(p)` statically for the same reason,
which is why the listing needs the `# type: ignore` to show the runtime failure.
A proxy that must forward special methods defines them explicitly.

`len(p)` reports the miss because nothing supplies a default `__len__()`.
`print(p)` cannot: `object` already defines `__str__()`,
so the lookup on `type(p)` finds that one and the proxy prints as itself.
A bypassed dunder that `object` defines fails silently,
with no error pointing at the miss.

Delegation forwards reads, not writes:

```python
# proxy_writes.py
from typing import Any

class Settings:
    def __init__(self) -> None:
        self.level = "low"

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

settings = Settings()
p = Proxy(settings)
print(p.level)
#: low
p.level = "high"  # type: ignore
print(p.level, settings.level)
#: high low
```

`__getattr__()` is a read hook.
The assignment stores `level` on the proxy, where the next lookup finds it,
so the proxy stops consulting the implementation and the two disagree.
The type checker objects to the assignment,
because `Proxy` declares no `level` and no `__setattr__()` to accept one,
which is the static half of the same warning.
A surrogate that must forward writes defines `__setattr__()` as well,
and that method must let the proxy's own attributes through,
or the assignment in `__init__()` recurses:

```python
# proxy_setattr.py
from typing import Any

class Settings:
    def __init__(self) -> None:
        self.level = "low"

class WriteProxy:
    def __init__(self, impl: Any) -> None:
        object.__setattr__(self, "_impl", impl)
    def __getattr__(self, name: str) -> Any:
        return getattr(self._impl, name)
    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._impl, name, value)

settings = Settings()
p = WriteProxy(settings)
p.level = "high"
print(p.level, settings.level)
#: high high
```

`object.__setattr__()` stores `_impl` directly on the proxy,
going around the `__setattr__()` that would otherwise forward it to an implementation that does not exist yet.
Every assignment after that reaches the implementation,
so the two no longer disagree.
The `# type: ignore` that `proxy_writes.py` needed disappears here:
declaring `__setattr__()` tells the checker the proxy accepts arbitrary attributes,
so the static half closes at the same moment as the runtime half.

Identity has the same gap.
A proxy is not an instance of the implementation's class;
delegation forwards the methods, not the type.
A `@runtime_checkable` `Protocol` does not close that gap either.
Since Python 3.12 that check uses `inspect.getattr_static()`,
which reads the class and instance dictionaries directly and does not call `__getattr__()`,
so a proxy whose methods all arrive through delegation fails it too.
Ordinary attribute access still finds those methods,
so `hasattr(p, "f")` is `True` and `p.f()` runs.
Code that calls the method, or probes with `hasattr()`, works on a surrogate;
code that asks `isinstance()` sees only the proxy's own class.

```python
# proxy_identity.py
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class Service(Protocol):
    def f(self) -> None: ...

class Implementation:
    def f(self) -> None: print("Implementation.f()")

class Proxy:
    def __init__(self) -> None:
        self.__implementation = Implementation()
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy()
p.f()
#: Implementation.f()
print(hasattr(p, "f"))
#: True
print(isinstance(p, Implementation), isinstance(p, Service))
#: False False
```

The call works and `hasattr()` finds the method,
yet neither check recognizes the proxy.

Two escapes exist, and each makes `isinstance()` answer a question nothing verified.
`Service.register(Proxy)` tells the ABC machinery to answer `True` without checking anything,
and a `__class__` property returning the implementation's class makes `isinstance()` answer for the wrong object.
Each satisfies the runtime check and neither satisfies a type checker.
A surrogate is not its implementation,
and code that needs it to be should ask for a method instead.

## State

The *State* pattern adds more implementations to *Proxy*,
along with a way to switch from one implementation to another during the lifetime of the surrogate:

```python
# state.py
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
Only the object behind the surrogate does.

The annotations that carry the implementation are all `Any`,
which the book's typing guidance treats as a last resort.
The reason is the one the Proxy section gave:
whatever `__getattr__()` returns is unknown at the type level,
so no checker can verify `b.f()`, no matter how you annotate the surrogate.
Declaring each implementation against `Behavior` still catches a missing method,
because the checker verifies that `Implementation1` and `Implementation2` have everything `run()` calls.
That declaration stops at the surrogate.
Annotating `run(b: Behavior)` and handing it `b` is a type error,
because `Surrogate` defines no `f()` of its own.
The hop through the surrogate loses the guarantee.

Testing hands the State surrogate a small stand-in and confirms calls reach the current implementation,
and that `change_to()` swaps it:

```python
# test_state.py
from state import Surrogate

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

## Kinds of Proxy

The difference between *Proxy* and *State* is in the problem each one solves.
The common uses for *Proxy* as described in *GoF Design Patterns* are:

1.  *Remote proxy*.
    Proxies for an object in a different address space.
    Distributed-object systems generate these.
    In Python, remote procedure call (RPC) libraries play this role.
2.  *Virtual proxy*.
    Provides "lazy initialization" to create expensive objects on demand.
3.  *Protection proxy*.
    Use this when you don't want the client programmer to have full access to the proxied object.
4.  *Smart reference*.
    Adds actions when code accesses the proxied object.
    For example, to keep track of the number of references held for a particular object,
    to implement the *copy-on-write* idiom and prevent object aliasing.
    A simpler example is keeping track of the number of calls to a particular method.

A *Protection proxy* decides whether a call reaches the implementation.
`__getattr__()` receives the requested name, so the check is one condition:

```python
# protection_proxy.py
from typing import Any, Final

READ_ONLY: Final[frozenset[str]] = frozenset({"read"})

class Document:
    def read(self) -> str: return "contents"
    def erase(self) -> None: print("erased")

class Guarded:
    def __init__(self, doc: Document, *, admin: bool) -> None:
        self._doc = doc
        self._admin = admin
    def __getattr__(self, name: str) -> Any:
        if not self._admin and name not in READ_ONLY:
            raise PermissionError(name)
        return getattr(self._doc, name)

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
a decorator adds behavior around a call it always makes,
while this proxy decides whether the call goes through.

A *Smart reference* proxy adds behavior around each access without refusing any.
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

Because `__getattr__()` intercepts only the lookups not found on the proxy or its class,
one generic proxy can add lazy initialization (a *virtual proxy*), access checks
(a *protection proxy*), or call tracking (a *smart reference*) to any object,
with no per-method code.

`CountingProxy` uses single underscores rather than the earlier proxies' `self.__implementation`,
so the trap below can misspell `self._imp` without name mangling obscuring the typo.

The fallback hook has a trap of its own:
if `__getattr__()`'s body touches a proxy attribute that does not exist,
a misspelled `self._imp`,
or any attribute on an instance built without `__init__()`,
which `copy.copy()` and `pickle` do when they rebuild one,
that failed lookup calls `__getattr__()` again,
and the error surfaces as `RecursionError`,
not the `AttributeError` that would point at the typo.

The counting proxy's test confirms that a call reaches the implementation and returns its result,
and that it counts calls without counting an attribute read:

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

## One Surrogate, Two Intents

*GoF Design Patterns* gives *Proxy* and *State* different structures and so treats them as unrelated.
But both are a *Surrogate*:
a front object that passes method calls through to an implementation.
*Proxy* fronts for one implementation to control access to it.
*State* swaps among several to change behavior over time.
In Python both are the same few lines of `__getattr__()` delegation,
with *State* adding a method to change the implementation.
The separate implementation hierarchy that *GoF Design Patterns* uses matters when other people write the implementations and you need the base class to state what they owe you.
When you write both sides,
the single generic surrogate above is simpler and just as flexible.

## Exercises

1.  Create an example of the "virtual proxy."
2.  Change `CountingProxy` in `counting_proxy.py` to keep a per-method tally in a `collections.Counter` instead of a single total.
    Confirm the tally reports `f` called twice and `g` called once.
3.  Create a simple copy-on-write implementation.
4.  In `counting_proxy.py`,
    misspell `self._impl` as `self._imp` inside `__getattr__()` and run it.
    Explain why the failure reports as `RecursionError` rather than an `AttributeError` naming the typo,
    using the fallback-hook behavior described in this chapter.
5.  Create a program similar to certain DBMS systems that allow only a fixed number of connections at any time.
    Implement this with a singleton-like system ([Singleton](24_Singleton.md))
    that controls the number of "connection" objects it creates.
    When a user finishes with a connection,
    the system must check that connection back in for reuse.
    To guarantee this, hand out a proxy instead of a reference to the actual connection,
    and design the proxy to release the connection back to the system.
6.  `dunder_bypass.py`'s `Proxy` cannot answer `len(p)`.
    Give it a `__len__()` that forwards to the implementation,
    and confirm `len(p)` returns 2.
    Then explain why `__getattr__()` could not have supplied it.
7.  Extend `Surrogate` in `state.py` so `change_to()` rejects an implementation missing a method the current one has,
    and explain why the type checker could not have caught that swap.
