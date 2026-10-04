# Surrogate: Solutions

## 1. A virtual proxy that answers the cheap requests itself

> Extend `virtual_proxy.py`'s `Lazy` so it answers one cheap attribute itself,
> a `description` string given at construction, without building `Expensive`.
> Count the accesses it answers that way,
> and report the count when `Lazy` builds `Expensive`.
> Confirm that reading `description` several times builds nothing,
> and that the first `query()` reports the count.

<details>
<summary>Where to look</summary>

[Virtual Proxy](../../Chapters/26_Patterns--Surrogate.md#virtual-proxy) builds `Expensive` inside `__getattr__()`, which runs only when normal lookup fails.
Give `Lazy` a property for the cheap attribute, so Python finds it on the class and skips the fallback.
Increment a counter in that property, and print the counter at the moment the fallback builds the real object.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Any

class Expensive:
    def __init__(self) -> None:
        ...

    def query(self) -> str:
        ...

class Lazy:
    def __init__(self, description: str) -> None:
        ...

    @property
    def description(self) -> str:
        ...

    def __getattr__(self, name: str) -> Any:
        ...
```

<details>
<summary>Solution</summary>

If you store `description` as an ordinary instance attribute,
normal lookup finds it and the three reads build nothing,
but no code runs on a read.
The counter stays at zero, so the first `query()` reports `0 answered before build`.
A property runs a method on each read,
so the solution counts there without reaching `__getattr__()`.

```python
# exercise_1.py
from typing import Any

class Expensive:
    def __init__(self) -> None:
        print("Expensive built")

    def query(self) -> str:
        return "result"

class Lazy:
    def __init__(self, description: str) -> None:
        self._description = description
        self._answered = 0
        self._real: Expensive | None = None

    @property
    def description(self) -> str:
        self._answered += 1
        return self._description

    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            print(f"{self._answered} answered before build")
            self._real = Expensive()
        return getattr(self._real, name)

p = Lazy("a slow query")
for _ in range(3):
    print(p.description)
#: a slow query
#: a slow query
#: a slow query
print(p.query())
#: 3 answered before build
#: Expensive built
#: result
print(p.query())
#: result
```

**Answer the cheap request without building.** `description` is a property on the proxy, so Python finds it without
calling `__getattr__()`, and the three reads build nothing. Each one
increments `_answered`.

**Build the real object on demand.** The first `query()` is the first name the proxy
lacks, so `__getattr__()` runs, reports the count, and builds the real
object. The second `query()` finds `_real` set and forwards without
reporting or building.

The counter records how much work the proxy saved: three
requests served from a string the proxy held from the start, with the
slow construction pushed past all of them. GoF's image proxy is the
same design, answering an image's size from stored numbers while the
pixels stay unloaded until something draws them.

</details>
</details>
</details>

## 2. A per-method tally in the counting proxy

> Change `CountingProxy` in `counting_proxy.py` to keep a per-method tally in a `collections.Counter` instead of a single total.
> Confirm the tally reports `f` called twice and `g` called once.

<details>
<summary>Where to look</summary>

[Smart Reference](../../Chapters/26_Patterns--Surrogate.md#smart-reference) wraps each forwarded call to count it.
`__getattr__()` receives the attribute name, so use it as the key into a `collections.Counter` in place of the single total.
Increment the entry inside the wrapper, before forwarding the call.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections import Counter
from typing import Any

class Implementation:
    def f(self) -> None: ...
    def g(self) -> None: ...

class CountingProxy:
    def __init__(self, impl: Any) -> None:
        ...

    def __getattr__(self, name: str) -> Any:
        ...
```

<details>
<summary>Solution</summary>

If you increment `self.calls[name]` in `__getattr__()` before the `callable()` test,
the demo still prints `2 1`, because each lookup there leads to one call.
A lookup without a call counts too.
Evaluating `p.f is p.f` adds two to `f`'s tally.
The solution counts inside `counted`,
so the tally advances at the call, as it does in the chapter's `CountingProxy`.

```python
# exercise_2.py
from collections import Counter
from typing import Any

class Implementation:
    def f(self) -> None: print("f()")
    def g(self) -> None: print("g()")

class CountingProxy:
    def __init__(self, impl: Any) -> None:
        self._impl = impl
        self.calls: Counter[str] = Counter()

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._impl, name)
        if callable(attr):
            def counted(*args: Any, **kwargs: Any) -> Any:
                self.calls[name] += 1
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
print(p.calls["f"], p.calls["g"])
#: 2 1
```

**Tally each call by name.** Where the chapter's `CountingProxy` keeps one total, this one tallies
per method name. `__getattr__()` receives the name of the
attribute, so the wrapper charges the count to that name before
forwarding. The single `calls` integer becomes a `Counter`. The final
`print()` shows `f` called twice and `g` once.

</details>
</details>
</details>

## 3. A simple copy-on-write list

> Create a simple copy-on-write list.
> Its `share()` returns a second list over the same data,
> at the cost of incrementing a reference count,
> and the first `append()` through a shared list copies the data before changing it.
> Confirm that the two lists share their data before the write and not after it.

<details>
<summary>Where to look</summary>

[Smart Reference](../../Chapters/26_Patterns--Surrogate.md#smart-reference) shows a surrogate doing extra work around each use of an implementation.
Keep the data and a count of owners together in one small shared object, and let `share()` hand out the same object with the count raised.
Have `append()` check the count and, when more than one owner exists, copy the data into a new object first.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Sequence
from dataclasses import dataclass

@dataclass
class Box:
    data: list[object]
    owners: int = 1

class CowList:
    def __init__(self, data: Sequence[object] | None = None,
                 _box: Box | None = None) -> None:
        ...

    def share(self) -> CowList:
        ...

    def append(self, item: object) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __repr__(self) -> str:
        ...
```

<details>
<summary>Solution</summary>

If you build the private `Box` around `self._box.data` without the `list(...)` copy,
`b` gets a `Box` of its own that holds the same list.
`b.append(4)` then changes `a` too.
The demo prints `[1, 2, 3, 4] [1, 2, 3, 4]`
while `a._box is b._box` reports `False`.
A new `Box` gives `b` its own owner count but not its own data,
so the solution copies the list before the write.

```python
# exercise_3.py
from collections.abc import Sequence
from dataclasses import dataclass

@dataclass
class Box:
    data: list[object]
    owners: int = 1

class CowList:
    def __init__(self, data: Sequence[object] | None = None,
                 _box: Box | None = None) -> None:
        self._box = (
            _box if _box is not None
            else Box(list(data or [])))

    def share(self) -> CowList:
        self._box.owners += 1
        # Shares the same Box, for now
        return CowList(_box=self._box)

    def append(self, item: object) -> None:
        if self._box.owners > 1:
            # Shared Box: copy before mutating
            self._box.owners -= 1
            self._box = Box(list(self._box.data))
        self._box.data.append(item)

    def __len__(self) -> int:
        return len(self._box.data)

    def __repr__(self) -> str:
        return repr(self._box.data)

a = CowList([1, 2, 3])
b = a.share()
print(a._box is b._box, a._box.owners)
#: True 2
b.append(4)
print(a, b)
#: [1, 2, 3] [1, 2, 3, 4]
print(a._box is b._box)
#: False
```

**Share the data and count its owners.** `a` and `b` start out sharing one `Box`, the same underlying list, with
`owners` tracking how many `CowList`s point at that `Box`. `share()`
copies a reference and bumps a count.

**Copy before a shared write.** `append()` copies the data, and only when `owners > 1`. `b.append(4)`
detaches `b` into its own private `Box` holding a fresh copy of the
data, decrements the shared `Box`'s count (since `b` is no longer one
of its owners), then appends to that private copy. Since no one called
`a.append()`, `a` still points at the original, untouched `Box`. The
first write triggers the copy, and only the list that writes pays for
it.

</details>
</details>
</details>

## 4. Why the typo reports as `RecursionError`

> In `counting_proxy.py`,
> misspell `self._impl` as `self._imp` inside `__getattr__()` and run it.
> Use the fallback behavior this chapter describes to explain why the failure reports as `RecursionError` rather than an `AttributeError` naming the typo.

<details>
<summary>Where to look</summary>

[The Recursion Trap](../../Chapters/26_Patterns--Surrogate.md#the-recursion-trap) and [Forwarding with `__getattr__()`](../../Chapters/26_Patterns--Surrogate.md#forwarding-with-getattr) describe a method that Python calls only after normal lookup fails.
Trace what Python does when the first line inside that method reads a name that does not exist.
Use `expected()` from `exceptions` to catch the failure in the listing.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import Any
from exceptions import expected

class Implementation:
    def f(self) -> None: ...

class BrokenProxy:
    def __init__(self, impl: Any) -> None:
        ...

    def __getattr__(self, name: str) -> Any:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from typing import Any
from exceptions import expected

class Implementation:
    def f(self) -> None: print("f()")

class BrokenProxy:
    def __init__(self, impl: Any) -> None:
        self._impl = impl
        self.calls = 0

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._imp, name)  # Deliberate typo
        if callable(attr):
            def counted(*args: Any, **kwargs: Any) -> Any:
                self.calls += 1
                return attr(*args, **kwargs)
            return counted
        return attr

p = BrokenProxy(Implementation())
with expected(RecursionError):
    p.f()
#: [RecursionError] maximum recursion depth exceeded
```

Python finds no `f` on the instance or on `BrokenProxy`, so it calls
`__getattr__("f")`. That call starts by reading `self._imp`, which does
not exist either, so Python calls `__getattr__("_imp")`, which starts
by reading `self._imp`. Each attempt to report the missing attribute
creates another missing-attribute lookup, and the stack runs out before
Python can raise an `AttributeError`.

The trap is specific to the fallback method. `__getattr__()` runs only
when normal lookup fails, so any missing name it touches sends Python
straight back into `__getattr__()`. Reading `self._impl`, which
`__init__()` did assign, resolves normally without reaching
`__getattr__()`. That normal lookup is why the chapter's working
version is safe and `BrokenProxy` is not. A proxy whose `__init__()`
did not run (an instance built through `object.__new__()`, for
example) fails the same way on its first attribute access.

</details>
</details>
</details>

## 5. A connection pool that hands out proxies

> Create a program similar to a DBMS that allows only a fixed number of connections at a time.
> Implement this with a system modeled on [*Singleton*](../../Chapters/24_Patterns--Singleton.md)
> that controls the number of "connection" objects it creates.
> When a user finishes with a connection,
> the system must check that connection back in for reuse.
> To guarantee this, return a proxy instead of a reference to the actual connection,
> and design the proxy to release the connection back to the system.

<details>
<summary>Where to look</summary>

[Protection Proxy](../../Chapters/26_Patterns--Surrogate.md#protection-proxy) shows a surrogate that controls access to an implementation.
Let only a `Pool` class create the `Connection` objects, and have `acquire()` return a proxy that forwards through `__getattr__()`.
Make the proxy a context manager whose `__exit__()` returns the connection to the pool and drops its own reference.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from typing import Any, Final, Self
from exceptions import expect

POOL_SIZE: Final[int] = 2

class PoolExhausted(RuntimeError):
    "No connection is free."

class Connection:
    def __init__(self, number: int) -> None:
        ...

    def query(self, sql: str) -> str:
        ...

class Pool:
    def __init__(self, size: int) -> None:
        ...

    def available(self) -> int:
        ...

    def acquire(self) -> ConnectionProxy:
        ...

    def release(self, connection: Connection) -> None:
        ...

class ConnectionProxy:
    def __init__(self, pool: Pool,
                 connection: Connection) -> None:
        ...

    def __getattr__(self, name: str) -> Any:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, *exception: object) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the line in `__exit__()` that sets `_connection` to `None`,
the pool gets each connection back, but the proxy keeps its reference.
After both blocks end, `c1.query()` answers through connection 0,
and when a later `acquire()` lends connection 0 to another client,
both proxies query through it.
The solution clears the reference, so a released proxy raises a `RuntimeError` instead.

```python
# exercise_5.py
from typing import Any, Final, Self
from exceptions import expect

POOL_SIZE: Final[int] = 2

class PoolExhausted(RuntimeError):
    "No connection is free."

class Connection:
    def __init__(self, number: int) -> None:
        self.number = number

    def query(self, sql: str) -> str:
        return f"connection {self.number}: {sql}"

class Pool:
    def __init__(self, size: int) -> None:
        self._size = size
        self._free = [Connection(n) for n in range(size)]

    def available(self) -> int:
        return len(self._free)

    def acquire(self) -> ConnectionProxy:
        if not self._free:
            raise PoolExhausted(f"all {self._size} in use")
        return ConnectionProxy(self, self._free.pop(0))

    def release(self, connection: Connection) -> None:
        self._free.append(connection)

class ConnectionProxy:
    def __init__(self, pool: Pool,
                 connection: Connection) -> None:
        self._pool = pool
        self._connection: Connection | None = connection

    def __getattr__(self, name: str) -> Any:
        if self._connection is None:
            raise RuntimeError(
                "connection already released")
        return getattr(self._connection, name)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exception: object) -> None:
        if self._connection is not None:
            self._pool.release(self._connection)
            self._connection = None

pool = Pool(POOL_SIZE)
with pool.acquire() as c1:
    print(c1.query("select 1"))
    with pool.acquire() as c2:
        print(c2.query("select 2"))
        print("free:", pool.available())
        expect(PoolExhausted, pool.acquire)
    print("inner released:", pool.available())
#: connection 0: select 1
#: connection 1: select 2
#: free: 0
#: [PoolExhausted] all 2 in use
#: inner released: 1
print("outer released:", pool.available())
#: outer released: 2
```

**Limit who creates connections.** `Pool` builds every `Connection` in its constructor, and nothing else
creates one. `Pool` controls creation as a *Singleton* class does, with
the limit raised from one object to `POOL_SIZE`.

**Hand out a stand-in.** The client holds no `Connection`. `acquire()` hands back a
`ConnectionProxy`, which forwards `query()` through `__getattr__()`
and owns the one job the connection cannot do for itself: returning
that connection to the pool.

**Return the connection on exit.** The proxy is also a context manager
([Context Managers](../../Chapters/15_Techniques--Context_Managers.md)).
`__exit__()` runs whether the block ends normally or raises an
exception, so "must check that connection back in" becomes a guarantee.

**Refuse use after release.** `__exit__()` also drops the proxy's reference to the connection, so a
released proxy cannot keep using a connection that now belongs to
someone else. The check in `__getattr__()` reports that misuse instead
of letting two clients share one connection. `ConnectionProxy` is a
*protection proxy* and a *smart reference* at once. It controls access,
and it adds an action (the check-in) around each loan of the connection.

</details>
</details>
</details>

## 6. Forwarding `__len__()` explicitly

> `dunder_bypass.py`'s `Proxy` cannot answer `len(p)`.
> Give that `Proxy` a `__len__()` that forwards to the implementation,
> and confirm `len(p)` returns 2.
> Then explain why `__getattr__()` could not have supplied it.

<details>
<summary>Where to look</summary>

[Special Methods Bypass `__getattr__()`](../../Chapters/26_Patterns--Surrogate.md#special-methods-bypass-getattr) explains why `len(p)` fails on a proxy that forwards only through `__getattr__()`.
Define `__len__()` on the proxy class and have it call `len()` on the implementation.
For the explanation, consider where `len()` looks for the method.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from typing import Any

class Words:
    def __init__(self) -> None:
        ...

    def __len__(self) -> int:
        ...

class Proxy:
    def __init__(self, impl: Any) -> None:
        ...

    def __getattr__(self, name: str) -> Any:
        ...

    def __len__(self) -> int:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from typing import Any

class Words:
    def __init__(self) -> None:
        self.items = ["spam", "eggs"]

    def __len__(self) -> int:
        return len(self.items)

class Proxy:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

    def __len__(self) -> int:
        return len(self.__implementation)

p = Proxy(Words())
print(len(p))
#: 2
```

`__getattr__()` could not have supplied `__len__()` because `len()`
does not look the name up on the instance. `len()` asks `type(p)` for
`__len__()` and calls what it finds there. That lookup skips the
instance, so no instance lookup fails, and a failed instance lookup is
the one event that calls `__getattr__()`. Python looks up every
implicitly invoked special method this way, so the method must exist on
the proxy's class.

**Forward the special method explicitly.** `__len__()` here delegates with `len(self.__implementation)` rather
than `self.__implementation.__len__()`. Both give the same answer, and
`len()` reads better. To forward many dunders, you write one such
method per dunder, or generate them in a loop over a list of names and
assign them onto the class.

</details>
</details>
</details>

## 7. A `change_to()` that refuses a narrower implementation

> Extend `Surrogate` in `state_surrogate.py` so `change_to()` rejects an implementation missing a method the current one has,
> and explain why the type checker could not have reported that swap.

<details>
<summary>Where to look</summary>

[*State*](../../Chapters/26_Patterns--Surrogate.md#state) swaps the implementation behind a surrogate with `change_to()`.
Build a set of public callable names with `dir()` and `getattr()` for the current implementation and for the new one.
Subtract the new set from the current one and raise a `TypeError` when anything remains.
For the explanation, consider what type the surrogate gives its implementation.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from typing import Any
from exceptions import expect

def methods(obj: object) -> set[str]:
    ...

class Surrogate:
    def __init__(self, implementation: Any) -> None:
        ...

    def change_to(self, new: Any) -> None:
        ...

    def __getattr__(self, name: str) -> Any:
        ...

class Full:
    def f(self) -> None: ...
    def g(self) -> None: ...

class Lacking:
    def f(self) -> None: ...
```

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from typing import Any
from exceptions import expect

def methods(obj: object) -> set[str]:
    return {
        name
        for name in dir(obj)
        if not name.startswith("_")
        and callable(getattr(obj, name))
    }

class Surrogate:
    def __init__(self, implementation: Any) -> None:
        self.__implementation = implementation

    def change_to(self, new: Any) -> None:
        missing = (methods(self.__implementation)
                   - methods(new))
        if missing:
            raise TypeError(f"missing: {sorted(missing)}")
        self.__implementation = new

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

class Full:
    def f(self) -> None: print("Full.f()")
    def g(self) -> None: print("Full.g()")

class Lacking:
    def f(self) -> None: print("Lacking.f()")

s = Surrogate(Full())
s.f()
#: Full.f()
expect(TypeError, s.change_to, Lacking())
#: [TypeError] missing: ['g']
s.g()  # The old implementation is still in place
#: Full.g()
```

**List the reachable methods.** `methods()` reports the public callables an object carries, the set a
caller can reach through the surrogate's `__getattr__()`.

**Refuse a narrower replacement.** `change_to()` compares the two sets and refuses the swap when the
replacement drops a name the current implementation answers. The
surrogate keeps its current implementation, so `s.g()` still works
after the rejected swap.

The type checker cannot make this decision. The decision compares
the type of the implementation the surrogate holds right now with the type of
the argument, and the checker knows neither. Both are `Any`, because
`__getattr__()` delegation deliberately leaves the implementation's
type untracked. Annotating both against a `Protocol` states a fixed
shape that every implementation must meet, a different guarantee. A
`Protocol` cannot express "at least what the last implementation had,"
because that comparison relates two runtime values rather than two
declarations.

</details>
</details>
</details>
