# Surrogate

> The caller talks to one object, and a different object behind it does the work.
> *Proxy* and *State* are both built on that stand-in,
> which this chapter calls a *Surrogate*.

Both *Proxy* and *State* provide a surrogate class that changes what happens behind a call without changing the calling code.
The surrogate hides the implementing class that does the work.
When you call a method in the surrogate,
the surrogate calls that method in the implementing class.
The two patterns are so similar that *Proxy* is a special case of *State*.

From a base class, derive the surrogate along with the class or classes that provide the implementation:

![*Surrogate* and each Implementation realize the same Interface](_images/surrogate)

This is the shape *GoF Design Patterns* gives *Proxy*.
Python does not need the shared base,
but the base is the clearest way to see what a surrogate is.

A surrogate goes wherever an implementation goes.
A surrogate object receives an implementation and forwards all method calls to it.
Both *Proxy* and *State* use that indirection: the surrogate can refuse a call,
delay creating the implementation, count or log the calls it forwards,
or swap the implementation for another.

Structurally, *Proxy* and *State* differ in one respect.
A *Proxy* forwards to one implementation for its whole life.
*State* switches among several.

## Proxy

### Explicit Forwarding

Here the *Proxy* drops the shared base and forwards each call by hand:

```python
# proxy_forwarding.py

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
`Proxy` qualifies as long as code calls it in place of the implementation.
That is a looser definition than in *GoF Design Patterns*,
and relies only on intent.
Under GoF's stricter definition, the interface separates *Proxy* from *Adapter*.
[Distinguishing the Wrappers](29_Patterns--Changing_the_Interface.md#distinguishing-the-wrappers)
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
from exceptions import expected

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
with expected(TypeError):
    Proxy(Partial())  # type: ignore
#: [TypeError] Can't instantiate abstract class Partial
#: without an implementation for abstract method 'g'
```

Because `Proxy` accepts any `Service` and `Complete` implements both methods,
the proxy can forward either call.
Because `Partial` omits `g()`,
constructing a `Partial` raises a `TypeError` before the first call.
The type checker reports that construction before the program runs,
so the line has a `# type: ignore` and the listing can show the runtime refusal.
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
A `Protocol` instead reports the mismatch statically,
at a parameter annotated `Service`, and needs no common base.
One caveat: `isinstance()` against a `@runtime_checkable` Protocol checks only that the methods exist,
not that their signatures match.
The static type checker verifies signatures.

### Forwarding with `__getattr__()` {#forwarding-with-getattr}

`__getattr__()` is Python's built-in delegation mechanism,
which [*Singleton*](24_Patterns--Singleton.md) uses to reach its inner object.
Delegating through it makes `Proxy` simpler to implement:

```python
# proxy_getattr.py
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
`Implementation` here has an `h()` that `proxy_forwarding.py`'s lacks,
and the proxy forwards `p.h()` with no change to `Proxy`.

The double underscore on `self.__implementation` matters:
the name [mangles](11_Techniques--Testing.md#white-box-and-black-box-tests)
to `_Proxy__implementation`,
so it cannot collide with an attribute the implementation defines.

Do not confuse `__getattr__()` with its lookalike, `__getattribute__()`.
`__getattr__()` is the *fallback* method:
Python calls it only after normal lookup fails.
Normal lookup finds `self.__implementation`,
so reading that name inside `__getattr__()` does not call it again.
`__getattribute__()` intercepts every attribute access,
including each `self.` access in its own body,
so a `__getattribute__()` that reads `self.__implementation` calls itself forever.
Writing a `__getattribute__()` means calling `object.__getattribute__()` for every internal access,
machinery a surrogate rarely needs.

`proxy_interface.py`'s abstract base class still guards the implementation side:
its `Proxy` takes a `Service` parameter,
so the type checker verifies that whatever you provide has the necessary methods.
A `Protocol` on that parameter guards the implementation side structurally,
and `proxy_protocol.py`'s `isinstance()` is the runtime half of that check.
Calls on the proxy get no such check.
Because `__getattr__()` resolves `p.f()` and returns `Any`,
the checker cannot verify that call.
A misspelled `p.ff()` passes the checker the same way,
and fails at runtime with the implementation's `AttributeError`.
With explicit forwarding, as in `proxy_forwarding.py`,
`p.f()` reaches a declared method with a declared return type,
and the checker verifies the call.
`proxy_interface.py`'s `Proxy` also passes as a `Service`:
because it inherits `Service`, code typed against `Service` accepts it.
`__getattr__()` gives up that check so it can forward every method,
including ones added later.

The lost static check is the first of five limits on `__getattr__()` delegation.
The next four sections cover the rest:
Python skips `__getattr__()` for a special-method lookup and for an assignment,
`__getattr__()` calls itself when the name it reads is also missing,
and a surrogate that supplies its methods through `__getattr__()` fails an `isinstance()` check.

### Special Methods Bypass `__getattr__()` {#special-methods-bypass-getattr}

Python looks up dunders like `__len__()` and `__str__()` on the proxy's type,
not on the instance, so `len(p)` and `print(p)` do not delegate,
while an explicit `p.__len__()` does:

```python
# dunder_bypass.py
from typing import Any
from exceptions import expect

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
# Special-method lookup skips the instance:
expect(TypeError, len, p)  # type: ignore
#: [TypeError] object of type 'Proxy' has no len()
print("__main__.Proxy object" in str(p))
#: True
```

`p.__len__()` and `len(p)` look interchangeable and are not.
`p.__len__()` is ordinary attribute access,
so the failed instance lookup falls through to `__getattr__()`, which delegates.
`len(p)` looks up `__len__()` on `type(p)`, skips the instance, finds none,
and reports that `Proxy` has no `len()`.
`ty` and Pyright reject `len(p)` statically for the same reason,
so the listing needs the `# type: ignore` to show the runtime failure.
Under mypy, `__getattr__()` also satisfies the lookup for `__len__()`,
so `len(p)` passes the check and fails only at runtime.
A proxy that must forward special methods defines them explicitly.

`len(p)` reports the missing method because `object` defines no `__len__()`.
`print(p)` reports no missing method: `object` defines `__str__()`,
so the lookup on `type(p)` finds `object`'s `__str__()` and the proxy prints as a `Proxy` object.
Whenever `object` defines the dunder, the bypass raises no error.
The proxy answers with `object`'s version instead of calling the implementation.

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

`__getattr__()` handles reads: Python calls it for a failed read,
not for an assignment.
The assignment stores `level` in the proxy's `__dict__`,
not the implementation's `__dict__`.
The next `p.level` lookup succeeds without calling `__getattr__()`.
The proxy reports `"high"` and the implementation reports `"low"`.
The type checker rejects the assignment because `Proxy` declares no `level` and no `__setattr__()` that accepts one.

To forward writes, define `__setattr__()`.
`__setattr__()` then intercepts every assignment,
including the one in `__init__()`.
Forwarding that first assignment recurses,
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

`WriteProxy` names its attribute `_implementation`, with one underscore.
Mangling rewrites identifiers, not string literals,
so storing a double-underscore name through `object.__setattr__()` means writing the mangled form,
`"_WriteProxy__implementation"`, by hand.
The single underscore costs the protection that mangling gives:
if the implementation has an `_implementation` of its own,
`p._implementation` finds the proxy's and the implementation's is out of reach.

### The Recursion Trap

`__getattr__()` can recurse.
If `__getattr__()`'s body reads a proxy attribute that does not exist,
the failed lookup calls `__getattr__()` again.
Python reports the recursion as a `RecursionError`,
not the `AttributeError` that names the cause.

A misspelled `self._implementation` is one cause.
Rebuilding a proxy through `copy.copy()` or `pickle` is another:
both construct the new instance without calling `__init__()`,
so no `_implementation` exists when the first failed lookup calls `__getattr__()`.
The fix is a guard at the top of `__getattr__()` that raises `AttributeError` for any name that starts with an underscore:

```python
# getattr_guard.py
from typing import Any
from exceptions import expected

class Proxy:
    def __init__(self, impl: Any) -> None:
        self._implementation = impl
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):  # The guard
            raise AttributeError(name)
        return getattr(self._imp, name)  # Deliberate typo

class Implementation:
    def f(self) -> None: print("Implementation.f()")

with expected(AttributeError):
    Proxy(Implementation()).f()
#: [AttributeError] _imp
```

Without the guard, the misspelled `self._imp` produces a `RecursionError` that names nothing.
With the guard, the second call to `__getattr__()` reports the typo by name.
The guard also makes the proxy work with `copy` and `pickle`,
which look up `__setstate__()` on an instance whose `__init__()` has not run.
Both get an `AttributeError`, which those modules handle, instead of recursing.

This chapter's other `__getattr__()` proxies do not include the guard,
so each listing shows one idea.

### A Surrogate Is Not Its Implementation

A proxy is not an instance of the implementation's class.
Delegation forwards the methods, not the type,
and `isinstance()` checks only the proxy's own class.
A `@runtime_checkable` `Protocol` does not change that.
Since Python 3.12 the Protocol check uses `inspect.getattr_static()`,
which reads the class and instance dictionaries instead of running attribute lookup.
That function bypasses `__getattr__()`,
so a proxy that supplies every method through `__getattr__()` also fails the `isinstance()` check:

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

Ordinary attribute access falls back to `__getattr__()`,
so `p.f()` runs and `hasattr(p, "f")` is `True`.
Both `isinstance()` checks return `False`.

Code that calls the method, or checks with `hasattr()`, works on a surrogate,
as long as `__getattr__()` raises only `AttributeError` for a name it does not have.
The [protection proxy](#protection-proxy) below raises a different exception,
and its section shows what `hasattr()` does with it.

Two workarounds make `isinstance()` return `True`,
and neither verifies anything:

-   `Service.register(Proxy)` tells the ABC machinery to answer `True` for every `Proxy`,
    without looking at its methods.
-   A `__class__` property returning the implementation's class makes `isinstance()` see that class rather than `Proxy`.

Both satisfy the runtime check and neither satisfies a type checker.
Inheritance satisfies both checks.
`proxy_interface.py`'s `Proxy` inherits `Service`,
so `isinstance(p, Service)` returns `True`,
and the type checker confirms that `Proxy`'s `f()` and `g()` match `Service`.
Forwarding through `__getattr__()` gives up both.
A surrogate is not its implementation,
and code that checks with `isinstance()` should check for the method instead.

## What Proxy Solves

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
    For example, a smart reference can log the calls to a particular method.
    It can also count the references to an object,
    which makes *copy-on-write* possible:
    copies share one object until one of them writes,
    and the writer then gets a copy of its own.

The standard library's `weakref.proxy()` is a transparent forwarding wrapper too,
but it solves none of these four:
it forwards to a weakly referenced object and raises `ReferenceError` once nothing else holds a strong reference to that object.
[Cleanup](10_Foundations--Cleanup.md#reliable-alternatives)
uses `weakref.ref()`,
and its [Watching Objects Without Holding Them](10_Foundations--Cleanup.md#watching-objects-without-holding-them)
section uses a `WeakValueDictionary`.
Both come from the same module, and neither needs `weakref.proxy()`.

### Virtual Proxy

A *virtual proxy* delays building an expensive object until something asks for it:

```python
# virtual_proxy.py
from typing import Any

class Expensive:
    def __init__(self) -> None:
        print("Expensive built")
    def query(self) -> str:
        return "result"

class Lazy:
    def __init__(self) -> None:
        self._real: Expensive | None = None
    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            self._real = Expensive()
        return getattr(self._real, name)

p = Lazy()
print("proxy ready")
#: proxy ready
print(p.query())
#: Expensive built
#: result
```

Building `Lazy` prints nothing.
`__getattr__()` builds `Expensive` on the first forwarded access,
and every later access reuses that same instance.

### Protection Proxy

A *protection proxy* decides whether a call reaches the implementation.
Because `__getattr__()` receives the requested name, the check is one condition:

```python
# protection_proxy.py
from typing import Any, Final
from exceptions import expect, expected

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
with expected(PermissionError):
    guest.erase()
#: [PermissionError] erase
expect(PermissionError, hasattr, guest, "erase")
#: [PermissionError] erase
Guarded(Document(), admin=True).erase()
#: erased
```

A guest reaches only the names in `READ_ONLY`, so `erase()` requires `admin`.
The protection is a convention, like the underscore on `_doc`:
`guest._doc.erase()` reaches the document without asking the proxy.
A protection proxy guards against mistakes,
not against a caller who goes around it.

`hasattr()` catches only `AttributeError`.
`guest.__getattr__()` raises `PermissionError` instead,
so `hasattr(guest, "erase")` raises `PermissionError` too,
where a missing name returns `False`.
A surrogate whose `__getattr__()` can raise something other than `AttributeError` breaks `hasattr()`.
The surrogate fails `isinstance()` for a different reason:
as [A *Surrogate* Is Not Its Implementation](#a-surrogate-is-not-its-implementation)
explains, the Protocol check uses `inspect.getattr_static()`,
which bypasses `__getattr__()`.

### Smart Reference

A *smart reference* proxy adds behavior around each access.
With `__getattr__()` you can wrap every method call, for example to count them:

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
    print(p.f is p.f, p.f.__name__)
    print("calls:", p.calls)
#: f()
#: g()
#: f()
#: False counted
#: calls: 3
```

`__getattr__()` returns a value, and here that value is a new function.
`counted` closes over `attr`, the implementation's bound method,
so the tally advances at the call, not at the lookup.
An attribute that is not callable returns unchanged,
so reading a data attribute counts nothing.

Lookup fails on every `p.f`, so every access builds another `counted`.
Two lookups of the same name therefore produce two different objects,
and the wrapper reports its own name, `counted`, rather than `f`.
Building a `counted` increments nothing.
Only a call to `counted` increments the tally,
so the three lookups in the `print()` leave the tally at three.

This proxy names its implementation `_impl`, with one underscore,
and so gives up the mangling that keeps `proxy_getattr.py`'s attribute from colliding.
`_impl` and `calls` now share a namespace with the implementation's own attributes:
reading `calls` from the proxy gives the counter,
even when the implementation defines a `calls` of its own.

Python calls `__getattr__()` for any name the proxy and its class lack,
but not for the proxy's own attributes.
The proxy therefore names no method of the implementation while still keeping state of its own.
The same few lines serve lazy initialization (a *virtual proxy*), access checks
(a *protection proxy*), or call tracking (a *smart reference*), over any object.

The tests confirm that a call reaches the implementation and returns its result,
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
from typing import Any

class Surrogate:
    def __init__(self, implementation: Any) -> None:
        self.__implementation = implementation
    def change_to(self, new_implementation: Any) -> None:
        self.__implementation = new_implementation
    # Delegate calls to the implementation:
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)
```

The demo gives the surrogate two implementations of one Protocol and swaps them mid-run:

```python
# state_demo.py
from typing import Any, Protocol
from state_surrogate import Surrogate

class Behavior(Protocol):
    def f(self) -> None: ...
    def g(self) -> None: ...
    def h(self) -> None: ...

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

first: Behavior = Implementation1()
second: Behavior = Implementation2()
b = Surrogate(first)
run(b)
#: Fiddle de dum, Fiddle de dee,
#: Eric the half a bee.
#: Ho ho ho, tee hee hee,
#: Eric the half a bee.
b.change_to(second)
run(b)
#: We're Knights of the Round Table.
#: We dance whene'er we're able.
#: We do routines and chorus scenes
#: We dance whene'er we're able.
```

The two calls to `run(b)` print different verses,
though neither `run()` nor `b` changes between them.
The figure follows `b.f()` through each step:

![](_images/surrogate_story)

The first frame alone is a *Proxy*.
The second and third show what *State* adds:
one assignment inside `change_to()` moves the arrow out of `__implementation`,
and the same `__getattr__()` forwarding then reaches the other implementation.
Only the surrogate's current implementation changes.
Here the client programmer calls `change_to()`,
but in a [*State Machine*](31_Patterns--State_Machines.md),
each implementation chooses its own successor,
so the surrogate advances without the client asking.
`change_to()` reassigns `__implementation` with no lock.
While one thread runs a multi-call sequence like `run()`,
another thread's `change_to()` can run between two of those calls,
splitting the sequence across both implementations;
see [Concurrency](19_Techniques--Concurrency.md#the-gil-does-not-prevent-races)
for what an unsynchronized swap costs.

`run(b: Any)` has no alternative.
Annotating `run(b: Behavior)` and passing it `b` is a type error,
because `Surrogate` defines no `f()` of its own.
As [Forwarding with `__getattr__()`](#forwarding-with-getattr) explains,
the checker cannot verify a method that `__getattr__()` supplies.

The test passes the *State* surrogate a small stand-in and confirms that calls reach the current implementation and that `change_to()` swaps it:

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

Every annotation in `state_surrogate.py` that carries the implementation is `Any`,
which the book's typing guidance treats as a last resort.
`__getattr__()` returns `Any` because it answers for whatever name the caller asks.
The `Any` on the parameters of `__init__()` and `change_to()` is a choice.
`state_demo.py` would still type-check if both parameters carried `Behavior`,
and the checker would then verify every implementation that reaches either method.
That annotation also ties the surrogate to one Protocol,
and the generic surrogate exists to avoid that tie.
`test_state.py` passes the same `Surrogate` a two-state stand-in that has a `name()` and none of `Behavior`'s three methods.
With `Behavior` on those parameters, `ty` rejects that test:
`type StateA is not assignable to protocol Behavior`.
Declaring the implementations as `first: Behavior` and `second: Behavior`,
as `state_demo.py` does,
puts the check where it does not restrict the surrogate.
The type checker verifies that `Implementation1` and `Implementation2` supply everything the Protocol declares,
and reports a missing method.
That declaration covers the implementations, not the surrogate.

## One Surrogate, Two Intents

Because *GoF Design Patterns* gives *Proxy* and *State* different structures,
it treats them as unrelated.
But both are a *Surrogate*:
an object that forwards method calls to an implementation.
*Proxy* controls access to a single implementation.
*State* swaps among several implementations to change behavior over time.
Both are the same few lines of `__getattr__()` delegation,
with *State* adding a method to change the implementation.
The separate implementation hierarchy in *GoF Design Patterns* matters when other people write the implementations and you need the base class to state which methods an implementation must supply.
When you write both sides,
the single generic surrogate in `state_surrogate.py` is simpler and just as flexible.

## Exercises

This chapter's [solutions](../Solutions/26_Patterns--Surrogate/) give a hint,
usually the shape of the code, and a full answer for each exercise.

1.  Extend `virtual_proxy.py`'s `Lazy` so it answers one cheap attribute itself,
    a `description` string given at construction, without building `Expensive`.
    Count the accesses it answers that way,
    and report the count when `Lazy` builds `Expensive`.
    Confirm that reading `description` several times builds nothing,
    and that the first `query()` reports the count.
2.  Change `CountingProxy` in `counting_proxy.py` to keep a per-method tally in a `collections.Counter` instead of a single total.
    Confirm the tally reports `f` called twice and `g` called once.
3.  Create a simple copy-on-write list.
    Its `share()` returns a second list over the same data,
    at the cost of incrementing a reference count,
    and the first `append()` through a shared list copies the data before changing it.
    Confirm that the two lists share their data before the write and not after it.
4.  In `counting_proxy.py`,
    misspell `self._impl` as `self._imp` inside `__getattr__()` and run it.
    Use the fallback behavior this chapter describes to explain why the failure reports as `RecursionError` rather than an `AttributeError` naming the typo.
5.  Create a program similar to a DBMS that allows only a fixed number of connections at a time.
    Implement this with a system modeled on [*Singleton*](24_Patterns--Singleton.md)
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
