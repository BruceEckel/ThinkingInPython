# Surrogate: Solutions

## 1. A virtual proxy: lazy creation of an expensive object

```python
# exercise_1.py
from typing import Any

class ExpensiveResource:
    def __init__(self) -> None:
        print("creating ExpensiveResource (slow!)")
        self.data = [1, 2, 3]

    def query(self) -> list[int]:
        return self.data

class LazyProxy:
    def __init__(self) -> None:
        self._real: ExpensiveResource | None = None

    def __getattr__(self, name: str) -> Any:
        if self._real is None:
            self._real = ExpensiveResource()
        return getattr(self._real, name)

print("proxy created, nothing built yet")
p = LazyProxy()
print("about to query")
print(p.query())
#: proxy created, nothing built yet
#: about to query
#: creating ExpensiveResource (slow!)
#: [1, 2, 3]
```

`"creating ExpensiveResource"` prints only when `p.query()` first
triggers `__getattr__()`, not when you construct `LazyProxy()`. Every
attribute access checks `self._real`, and the first access that finds
it `None` builds the real object. Every later access reuses the same
instance. `LazyProxy` reuses the `__getattr__()` delegation from
`proxy_2.py` and `counting_proxy.py`, just guarding the moment of
creation instead of forwarding to an object that already exists.

## 2. A per-method tally in the counting proxy

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
p.g()
p.f()
print(p.calls["f"], p.calls["g"])
#: f()
#: g()
#: f()
#: 2 1
```

Where the chapter's `CountingProxy` kept one total, this one tallies
per method name. `__getattr__()` already receives the name of the
attribute, so the wrapper charges the count to that name before
forwarding. The single `calls` integer becomes a `Counter`. The final
`print()` shows `f` called twice and `g` once.

## 3. A simple copy-on-write list

```python
# exercise_3.py
from collections.abc import Sequence

class Box:
    def __init__(self, data: list[object]) -> None:
        self.data = data
        self.owners = 1

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

`a` and `b` start out sharing one `Box`, the same underlying list, with
`owners` tracking how many `CowList`s point at that `Box`. `share()`
costs almost nothing: it copies a reference and bumps a count.
`append()` does the copying, and only when `owners > 1`. `b.append(4)`
detaches `b` into its own private `Box` holding a fresh copy of the
data, decrements the shared `Box`'s count (since `b` is no longer one
of its owners), then appends to that private copy. Since no one called
`a.append()`, `a` still points at the original, untouched `Box`. The
copy waits for a write and falls only on the list that writes, exactly
what "copy-on-write" means.

## 4. Why the typo reports as `RecursionError`

```python
# exercise_4.py
from typing import Any

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
try:
    p.f()
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
```

Python finds no `f` on the instance or on `BrokenProxy`, so it calls
`__getattr__("f")`. That call starts by reading `self._imp`, which does
not exist either, so Python calls `__getattr__("_imp")`, which starts
by reading `self._imp`. Each attempt to report the missing attribute
creates another missing-attribute lookup, and the stack runs out before
Python can raise an `AttributeError`.

The trap is specific to the fallback hook. `__getattr__()` runs only
when normal lookup fails, so any missing name it touches sends Python
straight back into `__getattr__()`. Reading `self._impl`, which
`__init__()` did assign, resolves normally and never reaches
`__getattr__()`. That is why the chapter's working version is safe and
`BrokenProxy` is not. A proxy whose `__init__()` never ran (an instance
built through `object.__new__()`, for example) fails the same way on
its first attribute access.

## 5. A connection pool that hands out proxies

```python
# exercise_5.py
from typing import Any, Final, Self

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
        try:
            pool.acquire()
        except PoolExhausted as e:
            print(type(e).__name__, e, pool.available())
    print("inner released:", pool.available())
print("outer released:", pool.available())
#: connection 0: select 1
#: connection 1: select 2
#: PoolExhausted all 2 in use 0
#: inner released: 1
#: outer released: 2
```

The client never holds a `Connection`. `acquire()` hands back a
`ConnectionProxy`, which forwards `query()` through `__getattr__()`
and owns the one job the connection cannot do for itself: returning
that connection to the pool. The proxy is also a context manager
([Context Managers](../Chapters/15_Techniques--Context_Managers.md)).
`__exit__()` runs whether the block ends normally or raises an
exception, so "must check it back in" becomes a guarantee.

`__exit__()` also drops the proxy's reference to the connection, so a
released proxy cannot keep using a connection that now belongs to
someone else. The check in `__getattr__()` reports that misuse instead
of letting two clients share one connection. `ConnectionProxy` is a
*protection proxy* and a *smart reference* at once: it controls access,
and it adds an action (the check-in) around the object's lifetime.

## 6. Forwarding `__len__()` explicitly

```python
# exercise_6.py
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

    def __len__(self) -> int:
        return len(self.__implementation)

p = Proxy()
print(len(p))
#: 2
```

`__getattr__()` could not have supplied `__len__()` because `len()`
never looks the name up on the instance. `len()` asks `type(p)` for
`__len__()` and calls what it finds there, skipping the instance
dictionary and therefore skipping `__getattr__()`, which only runs when
an instance lookup fails. Python looks up every implicitly invoked
special method this way, so the method must exist on the proxy's class.

`__len__()` here delegates with `len(self.__implementation)` rather
than `self.__implementation.__len__()`. Both give the same answer, and
`len()` reads better. To forward many dunders, you write one such
method per dunder, or generate them in a loop over a list of names and
assign them onto the class.

## 7. A `change_to()` that refuses a narrower implementation

```python
# exercise_7.py
from typing import Any

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
try:
    s.change_to(Lacking())
except TypeError as e:
    print(type(e).__name__, e)
#: TypeError missing: ['g']
s.g()  # The old implementation is still in place
#: Full.g()
```

`methods()` reports the public callables an object carries, the set a
caller can reach through the surrogate's `__getattr__()`.
`change_to()` compares the two sets and refuses the swap when the
replacement drops a name the current implementation answered. The
surrogate keeps what it had, so `s.g()` still works after the
rejected swap.

The type checker cannot make this decision. It would have to compare
the type of the value the surrogate holds right now against the type of
the argument. The surrogate's attribute is `Any`, because
`__getattr__()` delegation deliberately leaves the implementation's
type untracked. Annotating both against a `Protocol` states a fixed
shape that every implementation must meet, a different guarantee. A
`Protocol` cannot express "at least what the last implementation had,"
because that comparison relates two runtime values rather than two
declarations.
