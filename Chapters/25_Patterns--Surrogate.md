# Surrogate

> The caller talks to one object, and a different object behind it does the work.
> *Proxy* and *State* are both built on that stand-in,
> which this chapter calls a *Surrogate*.

Both *Proxy* and *State* provide a surrogate class that changes what runs behind a call while the calling code stays the same.
The surrogate hides the implementing class that does the work.
When you call a method in the surrogate,
the surrogate calls that method in the implementing class.
The two patterns are so similar that *Proxy* is a special case of *State*.

The surrogate and every implementing class derive from one base class:

![*Surrogate* and each Implementation realize the same Interface](_images/surrogate)

This is the shape *GoF Design Patterns* gives *Proxy*.
Python does not need the shared base, but the base shows, in one class,
the interface the surrogate shares with every implementation.

A surrogate object receives an implementation and forwards all method calls to it.
Code can therefore use a surrogate anywhere it uses an implementation.
The surrogate can refuse a call, delay creating the implementation,
count or log the calls it forwards, or swap the implementation for another.
Both *Proxy* and *State* use that indirection.

Structurally, *Proxy* and *State* differ in one respect.
A *Proxy* forwards to one implementation for its whole life.
*State* switches among several.

## Proxy

### Explicit Forwarding

Here the *Proxy* drops the shared base and forwards each call through a method of its own:

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

`Implementation` can have an interface different from `Proxy`'s interface.
`Proxy` still counts as a *Proxy* as long as code calls it in place of the implementation.
That definition is looser than the one in *GoF Design Patterns*,
because it depends only on how code uses `Proxy`.
Under GoF's stricter definition,
[the interface separates *Proxy* from *Adapter*](29_Patterns--Changing_the_Interface.md#distinguishing-the-wrappers).

A common interface helps, though.
`Implementation` must then supply every method that `Proxy` calls.
One way to express that interface is an abstract base class.
Each method the `Proxy` delegates to is an `@abstractmethod`,
so every implementation you can instantiate supplies them all:

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
    def __init__(self, impl: Service) -> None:
        self.__implementation = impl
    @override
    def f(self) -> None: self.__implementation.f()
    @override
    def g(self) -> None: self.__implementation.g()

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

The type checker reports the `Partial()` construction before the program runs,
so the line has a `# type: ignore` and the listing can show the runtime refusal.

The inheritance makes a `Proxy` acceptable wherever code expects a `Service`.
It also lets the type checker verify the `Proxy`'s `f()` and `g()` against the base.

A [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
is the structural alternative.
The implementation needs no base class.
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
A `Protocol` reports the mismatch statically,
at a parameter annotated `Service`, and needs no common base.

One caveat: `isinstance()` against a `@runtime_checkable` Protocol checks that the methods exist,
not that their signatures match.
The static type checker verifies signatures.

### Forwarding with `__getattr__()` {#forwarding-with-getattr}

`__getattr__()` is Python's built-in delegation mechanism,
which [*Singleton*](23_Patterns--Singleton.md)
uses to forward attribute access to its inner object.
Delegating through it replaces `Proxy`'s hand-written `f()` and `g()` with a single `__getattr__()`:

```python
# proxy_getattr.py
from typing import Any

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)
```

The demo gives this `Proxy` an implementation with three methods:

```python
# getattr_demo.py
from proxy_getattr import Proxy

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

`__getattr__()` makes the forwarding generic.
Because `Proxy` passes every name it lacks to the implementation,
it keeps working when you add a method to the implementation.

The double underscore on `self.__implementation` [mangles](11_Techniques--Testing.md#white-box-and-black-box-tests)
the name to `_Proxy__implementation`,
so it stays distinct from any attribute the implementation defines.

Do not confuse `__getattr__()` with its lookalike, `__getattribute__()`.
`__getattr__()` is the *fallback* method:
Python calls it only after normal lookup fails.
Normal lookup finds `self.__implementation`,
so reading that name inside `__getattr__()` returns the attribute.
`__getattribute__()` intercepts every attribute access,
including each `self.` access in its own body,
so a `__getattribute__()` that reads `self.__implementation` calls itself forever.
To avoid that recursion,
`__getattribute__()` must call `object.__getattribute__()` for every internal access.
A surrogate forwards only the names it lacks,
and `__getattr__()` receives exactly those,
so a surrogate rarely needs `__getattribute__()`.

The implementation side can keep its static check.
`proxy_getattr.py` annotates `impl` as `Any`.
A `__getattr__()` proxy can annotate it `Service`,
as `proxy_interface.py`'s `Proxy` does.
The type checker then verifies that the implementation you pass has the necessary methods.
A `Protocol` on that parameter guards the implementation side structurally.
`proxy_protocol.py`'s `isinstance()` is the runtime half of that check.

Calls on the proxy get no such check.
Because `__getattr__()` resolves `p.f()` and returns `Any`,
the checker accepts any call on `p`.
A misspelled `p.ff()` passes the checker the same way,
and fails at runtime with the implementation's `AttributeError`.
With explicit forwarding, as in `proxy_forwarding.py`,
`p.f()` reaches a declared method with a declared return type,
and the checker verifies the call.

`proxy_interface.py`'s `Proxy` also passes as a `Service`.
Because it inherits `Service`, code typed against `Service` accepts it.
A `__getattr__()` proxy gives up that check so it can forward every method,
including ones added later.

The lost static check is the first of five limits on `__getattr__()` delegation.
Python skips `__getattr__()` for a special-method lookup and for an assignment.
`__getattr__()` calls itself when the name it reads is also missing.
A surrogate that supplies its methods through `__getattr__()` fails an `isinstance()` check.

### Special Methods Bypass `__getattr__()` {#special-methods-bypass-getattr}

Python looks up dunders like `__len__()` and `__str__()` on the proxy's type,
not on the instance.
`len(p)` and `print(p)` therefore skip the delegation,
while a direct `p.__len__()` call delegates:

```python
# dunder_bypass.py
from exceptions import expect
from proxy_getattr import Proxy

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return " ".join(self.items)

w = Words()
p = Proxy(w)
print(p.__len__())  # The explicit call delegates
#: 2
# Special-method lookup skips the instance:
expect(TypeError, len, p)  # type: ignore
#: [TypeError] object of type 'Proxy' has no len()
print(w, "|", str(p).split(" at ")[0])
#: spam eggs | <proxy_getattr.Proxy object
```

`p.__len__()` and `len(p)` look interchangeable but take different lookup paths.
`p.__len__()` is ordinary attribute access.
That lookup searches the instance and `Proxy`, finds no `__len__()`,
and falls through to `__getattr__()`, which delegates.
`len(p)` looks up `__len__()` on `type(p)`, skips the instance, finds none,
and reports that `Proxy` has no `len()`.

`ty` and Pyright reject `len(p)` statically for the same reason,
so the listing needs the `# type: ignore` to show the runtime failure.
Under mypy, `__getattr__()` also satisfies the lookup for `__len__()`,
so `len(p)` passes the check and fails at runtime.

`len(p)` reports the missing method because `object` defines no `__len__()`.
`str(p)` succeeds.
`object` defines `__str__()`,
so the lookup on `type(p)` finds `object`'s version.
Whenever `object` defines the dunder,
Python calls `object`'s version instead of the implementation's version.
A proxy that must forward special methods therefore defines each one in its class body.

### Forwarding Writes

Delegation using `__getattr__()` forwards reads but not writes:

```python
# proxy_writes.py
from proxy_getattr import Proxy

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

Python calls `__getattr__()` as the fallback for a read and sends an assignment to `__setattr__()`,
which `Proxy` inherits from `object`.
`object.__setattr__()` stores `level` in the proxy's `__dict__`.
The implementation keeps its own `level`.
The next `p.level` lookup finds the proxy's `level`,
so Python skips `__getattr__()`.

The type checker rejects the assignment because `Proxy` declares no `level` and no `__setattr__()` that accepts one.

To forward writes, define `__setattr__()`.
`__setattr__()` then intercepts every assignment,
including the one in `__init__()`.
Forwarding that first assignment recurses,
because forwarding reads the attribute that the assignment is creating.
`__init__()` therefore stores the implementation another way:

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
`WriteProxy` needs no `# type: ignore`,
because a declared `__setattr__()` makes the type checker accept assignment to any attribute name.

`WriteProxy` names its attribute `_implementation`, with one underscore.
Mangling rewrites identifiers, not string literals.
To store a double-underscore name through `object.__setattr__()`,
you write the mangled form in the string literal,
`"_WriteProxy__implementation"`.
The single underscore keeps the name as written.
If the implementation has an `_implementation` of its own,
`p._implementation` finds the proxy's attribute,
which hides the implementation's attribute.

### The Recursion Trap

`__getattr__()` can recurse.
If `__getattr__()`'s body reads a proxy attribute that does not exist,
the failed lookup calls `__getattr__()` again.
Python reports the recursion as a `RecursionError`,
not the `AttributeError` that names the cause.

A misspelled `self._implementation` is one cause.
Rebuilding a proxy through `copy.copy()` or `pickle` is another.
`copy.copy()` and `pickle` both construct the new instance and skip `__init__()`,
so its `__dict__` is empty when the first failed lookup calls `__getattr__()`.
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

Without the guard, the misspelled `self._imp` produces a `RecursionError` that hides the typo.
With the guard, the second call to `__getattr__()` reports the typo by name.
The guard also makes the proxy work with `copy` and `pickle`,
which look up `__setstate__()` on an instance whose `__init__()` has not run.
Both get an `AttributeError`, treat it as a missing `__setstate__()`,
and copy the saved state into the new instance's `__dict__` instead of recursing.

The guard raises an `AttributeError` for every name that starts with an underscore,
though, including an implementation's `_helper()` and a direct `p.__len__()` call like the one in `dunder_bypass.py`.
A narrower guard, `if name == "_implementation"`,
keeps forwarding those names and still works with `copy` and `pickle`,
but a typo like `self._imp` recurses again.

This chapter's other `__getattr__()` proxies leave the guard out,
so each listing shows one idea.

### A Surrogate Is Not Its Implementation

A surrogate is not an instance of the implementation's class.
Delegation forwards the methods, not the type.
`isinstance()` checks only the proxy's own class.
A `@runtime_checkable` `Protocol` gives the same answer.
Since Python 3.12 the Protocol check uses `inspect.getattr_static()`,
which reads the class and instance dictionaries instead of running attribute lookup.
That function bypasses `__getattr__()`,
so a proxy that supplies every method through `__getattr__()` also fails the `isinstance()` check:

```python
# proxy_identity.py
from typing import Protocol, runtime_checkable
from proxy_getattr import Proxy

@runtime_checkable
class Service(Protocol):
    def f(self) -> None: ...

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

Code that calls the method, or checks with `hasattr()`, works on a surrogate,
as long as every exception `__getattr__()` raises is an `AttributeError`.
The [protection proxy](#protection-proxy) below raises a different exception,
and its section shows what `hasattr()` does with it.

Two workarounds make `isinstance()` return `True`,
and neither checks which methods the proxy supplies:

-   `Service.register(Proxy)` tells the ABC machinery to answer `True` for every `Proxy`,
    whatever methods it has.
-   A `__class__` property returning the implementation's class makes `isinstance()` test that class in place of `Proxy`.

Both workarounds satisfy the runtime check.
Neither satisfies a type checker.
Inheritance satisfies both checks.
`proxy_interface.py`'s `Proxy` inherits `Service`,
so `isinstance(p, Service)` returns `True`,
and the type checker confirms that `Proxy`'s `f()` and `g()` match `Service`.
Forwarding through `__getattr__()` gives up both.
Code that checks a surrogate with `isinstance()` should check for the method instead.

## What Proxy Solves

*GoF Design Patterns* lists these common uses for *Proxy*:

1.  *Remote proxy*.
    Proxies for an object in a different address space.
    Distributed-object systems generate these.
    In Python, remote procedure call (RPC) libraries provide them.
2.  *Virtual proxy*.
    Provides "lazy initialization" to create expensive objects on demand.
3.  *Protection proxy*.
    Restricts the client programmer's access to the implementation.
4.  *Smart reference*.
    Adds actions when code accesses the implementation.
    For example, a smart reference can log the calls to a particular method.
    It can also count the references to an object,
    which makes *copy-on-write* possible.
    Under copy-on-write, copies share one object until one of them writes,
    and the writer then gets a copy of its own.

The standard library's `weakref.proxy()` is a transparent forwarding wrapper too,
but it solves none of these four.
It forwards to a weakly referenced object and raises `ReferenceError` on any use after the last strong reference to that object goes away.

### Virtual Proxy

A virtual proxy delays building a slow-to-build object until the first attribute access on the proxy:

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
print(p.query())  # [1]
#: result
```

Building `Lazy` defers `Expensive`, so `proxy ready` prints first.
Every later access reuses the `Expensive` instance,
so the `query()` at `[1]` prints `result` alone.

### Protection Proxy

A protection proxy decides whether a call reaches the implementation.
Because `__getattr__()` receives the requested name,
the check is one `if` statement:

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

The protection is a convention, like the underscore on `_doc`.
Normal lookup finds `guest._doc`, so Python skips `__getattr__()` and its check,
and `guest._doc.erase()` reaches the document.
A protection proxy guards against mistakes,
not against a caller who reads `_doc`.

`hasattr()` catches `AttributeError` and lets every other exception propagate.
`guest.__getattr__()` raises `PermissionError`,
so `hasattr(guest, "erase")` raises `PermissionError` too,
where a missing name on an ordinary object returns `False`.
A surrogate fails `isinstance()` for a [different reason](#a-surrogate-is-not-its-implementation).

### Smart Reference

A smart reference proxy adds behavior around each access.
`__getattr__()` can wrap every method call, for example to count the calls:

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
```

The demo wraps an `Implementation` with two methods and calls through the proxy:

```python
# counting_demo.py
from counting_proxy import CountingProxy

class Implementation:
    def f(self) -> None: print("f()")
    def g(self) -> None: print("g()")

p = CountingProxy(Implementation())
p.f()
#: f()
p.g()
#: g()
p.f()
#: f()
print(p.f is p.f, p.f.__name__)
#: False counted
print("calls:", p.calls)
#: calls: 3
```

`counted` closes over `attr`, the implementation's bound method,
so `self.calls` increments when code calls `counted`,
not when `__getattr__()` returns it.

Normal lookup fails on every `p.f`,
so every access calls `__getattr__()` and builds another `counted`.
Building a `counted` leaves the tally alone,
so the `p.f is p.f` test and the `__name__` read leave it at three.

This proxy names its implementation `_impl`, with one underscore,
and so gives up the mangling that keeps `proxy_getattr.py`'s attribute from colliding.
`_impl` and `calls` now share a namespace with the implementation's own attributes.
Reading `calls` from the proxy gives the counter,
even when the implementation defines a `calls` of its own.

Python calls `__getattr__()` for a name the proxy and its class lack,
and finds the proxy's own attributes, such as `calls`, by normal lookup.
The proxy therefore keeps state of its own and forwards the methods the implementation has.
The same few lines serve lazy initialization (a virtual proxy), access checks
(a protection proxy), or call tracking (a smart reference), over any object.

The tests confirm that a call reaches the implementation and returns its result,
and that the proxy counts calls and leaves attribute reads out of the tally:

```python
# test_counting_proxy.py
from counting_proxy import CountingProxy

class Doubler:
    factor = 2
    def double(self, n: int) -> int:
        return n * self.factor

def test_proxy_forwards_call_and_result() -> None:
    p = CountingProxy(Doubler())
    assert p.double(5) == 10
    assert p.double(3) == 6

def test_proxy_counts_only_calls() -> None:
    p = CountingProxy(Doubler())
    assert p.factor == 2
    assert p.calls == 0
    p.double(1)
    p.double(1)
    assert p.calls == 2
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

def run(surrogate: Any) -> None:
    surrogate.f()
    surrogate.g()
    surrogate.h()

first: Behavior = Implementation1()
second: Behavior = Implementation2()
surrogate = Surrogate(first)
run(surrogate)
#: Fiddle de dum, Fiddle de dee,
#: Eric the half a bee.
#: Ho ho ho, tee hee hee,
surrogate.change_to(second)
run(surrogate)
#: We're Knights of the Round Table.
#: We dance whene'er we're able.
#: We do routines and chorus scenes
```

The two calls to `run(surrogate)` print different verses,
though `run()` and `surrogate` stay the same between them.
The figure follows `surrogate.f()` through each step:

![](_images/surrogate_story)

The first frame alone is a *Proxy*.
The second and third show what *State* adds.
One assignment inside `change_to()` rebinds `__implementation`.
The same `__getattr__()` forwarding then reaches the other implementation.
Only the surrogate's current implementation changes.

Here the client programmer calls `change_to()`,
but in a [*State Machine*](31_Patterns--State_Machines.md),
the client supplies an input and the machine chooses the next implementation,
so the client never specifies one.

`change_to()` reassigns `__implementation` with no lock.
While one thread runs a multi-call sequence like `run()`,
another thread's `change_to()` can run between two of those calls,
splitting the sequence across both implementations.
See [Concurrency](19_Techniques--Concurrency.md#the-gil-does-not-prevent-races)
for the races an unsynchronized swap allows.

`run()` takes `surrogate: Any` because a `Behavior` annotation fails at the call.
If `run()` declares `surrogate: Behavior`, the checker rejects `run(surrogate)`,
because `Surrogate` defines no `f()` of its own.
The checker [cannot verify a method that `__getattr__()` supplies](#forwarding-with-getattr).

The test passes the *State* surrogate two small implementations,
`StateA` and `StateB`,
and confirms that calls reach the current implementation and that `change_to()` swaps it:

```python
# test_state.py
from state_surrogate import Surrogate

class StateA:
    def name(self) -> str:
        return "A"

class StateB:
    def name(self) -> str:
        return "B"

def test_calls_reach_current_and_change_to_swaps() -> None:
    s = Surrogate(StateA())
    assert s.name() == "A"
    s.change_to(StateB())
    assert s.name() == "B"
```

Every annotation in `state_surrogate.py` that carries the implementation is `Any`,
which the book's typing guidance treats as a last resort.
`__getattr__()` returns `Any` because it returns the attribute for any name the caller reads,
whatever that attribute's type.
The `Any` on the parameters of `__init__()` and `change_to()` is a choice.
`state_demo.py` still type-checks if both parameters carry `Behavior`.
The checker then verifies every implementation that reaches either method.
That annotation also limits the surrogate to implementations of one Protocol,
but the generic surrogate exists to accept any implementation.
`test_state.py` passes the same `Surrogate` two implementations,
`StateA` and `StateB`,
each with a `name()` and none of `Behavior`'s three methods.
With `Behavior` on those parameters, `ty` rejects that test:
`type StateA is not assignable to protocol Behavior`.

`state_demo.py` declares the implementations as `first: Behavior` and `second: Behavior`.
That declaration checks the implementations and leaves the surrogate generic.
The type checker verifies that `Implementation1` and `Implementation2` supply everything the Protocol declares,
and reports a missing method.

A type parameter, `class Surrogate[T]`,
lets the surrogate accept any implementation type,
but the type checker infers `T` from the first implementation's class.
`Surrogate(StateA())` is a `Surrogate[StateA]`,
so the checker rejects `change_to(StateB())`.
With that surrogate, `state_demo.py` fails the same way.
`ty` narrows `first` to `Implementation1` despite its `Behavior` declaration,
and rejects `surrogate.change_to(second)`.
Every caller then writes the parameter out, as in `Surrogate[StateA | StateB]`,
so `state_surrogate.py` keeps `Any`.

## One Surrogate, Two Intents

Because *GoF Design Patterns* gives *Proxy* and *State* different structures,
it treats them as unrelated.
But both are a *Surrogate*:
an object that forwards method calls to an implementation.
*Proxy* controls access to a single implementation.
*State* swaps among several implementations to change behavior over time.
Both are the same few lines of `__getattr__()` delegation,
with *State* adding a method to change the implementation.

*GoF Design Patterns* gives *Proxy* a shared base,
written in `proxy_interface.py` as the `Service` ABC.
When other people write the implementations,
that base states which methods an implementation must supply,
and Python refuses to construct one that lacks any of them.
When you write both sides,
the single generic surrogate in `state_surrogate.py` forwards to any implementation with one `__getattr__()` and no base class.

## Exercises

Try each exercise before opening its [solution](../Solutions/25_Patterns--Surrogate/).

1.  Extend `virtual_proxy.py`'s `Lazy` so it answers one attribute itself,
    a `description` string given at construction, without building `Expensive`.
    Count the accesses it answers that way,
    and report the count when `Lazy` builds `Expensive`.
    Confirm that `Lazy` answers several reads of `description` before it builds `Expensive`,
    and that the first `query()` reports the count.
2.  Change `CountingProxy` in `counting_proxy.py` to keep a per-method tally in a `collections.Counter` instead of a single total.
    Confirm the tally reports `f` called twice and `g` called once.
3.  Create a simple copy-on-write list.
    Its `share()` returns a second list over the same data and increments a reference count.
    The first `append()` through a shared list copies the data before changing it.
    Confirm that the two lists share their data before the write and hold separate copies after it.
4.  In `counting_proxy.py`,
    misspell `self._impl` as `self._imp` inside `__getattr__()` and run `counting_demo.py`.
    Use the fallback behavior this chapter describes to explain why the failure reports as `RecursionError` rather than an `AttributeError` naming the typo.
5.  Create a program similar to a DBMS that allows only a set number of connections at a time.
    Implement this with a system modeled on [*Singleton*](23_Patterns--Singleton.md)
    that controls the number of "connection" objects it creates.
    When a user finishes with a connection,
    the system must check that connection back in for reuse.
    To guarantee this, return a proxy instead of a reference to the actual connection,
    and design the proxy to release the connection back to the system.
6.  `len(p)` raises a `TypeError` on the `Proxy` that `dunder_bypass.py` imports from `proxy_getattr.py`.
    Give that `Proxy` a `__len__()` that forwards to the implementation,
    and confirm `len(p)` returns 2.
    Then explain why `__getattr__()` could not have supplied it.
7.  Extend `Surrogate` in `state_surrogate.py` so `change_to()` rejects an implementation missing a method the current one has,
    and explain why the type checker could not have reported that swap.
