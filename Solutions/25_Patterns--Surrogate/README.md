# Surrogate: Solutions

## 1. A virtual proxy that answers the cheap requests itself

> Extend `virtual_proxy.py`'s `Lazy` so it answers one attribute itself,
> a `description` string given at construction, without building `Expensive`.
> Count the accesses it answers that way,
> and report the count when `Lazy` builds `Expensive`.
> Confirm that `Lazy` answers several reads of `description` before it builds `Expensive`,
> and that the first `query()` reports the count.

<details>
<summary>Where to look</summary>

[Virtual *Proxy*](../../Chapters/25_Patterns--Surrogate.md#virtual-proxy)
builds `Expensive` inside `__getattr__()`,
which runs only when normal lookup fails.
Give `Lazy` a property for `description`,
so Python finds it on the class and skips the fallback.
Increment a counter in that property,
and print the counter at the moment the fallback builds the real object.

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
<summary>Done when</summary>

your `exercise_1.py` prints the `description` three times before any build message appears,
and the first `query()` then prints `3 answered before build` ahead of `Expensive built`.
A second `query()` prints its result with no count and no build.

<details>
<summary>Solution</summary>

If you store `description` as an ordinary instance attribute,
normal lookup finds it, so the build still waits for `query()`.
Each read returns the stored string, though, so the counter stays at zero.
The first `query()` then reports `0 answered before build`.
A property also stops the lookup at the class, before `__getattr__()`,
and it runs a method on each read, so the solution counts inside that method.

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
print(p.query())  # [1]
#: 3 answered before build
#: Expensive built
#: result
print(p.query())  # [2]
#: result
```

**Answer `description` without building.**
`description` is a property of `Lazy`,
so normal lookup finds it on the class and stops there.

**Build the real object on demand.**
At `[1]`, `query` is the first name missing from the proxy,
so `__getattr__()` runs and builds the real object.
At `[2]`, `__getattr__()` runs again and finds `_real` set.

The proxy serves three requests from a string it holds from the start and defers the slow construction until the first `query()`.
GoF's image proxy is the same design.
It answers an image's size from stored numbers and loads the pixels when something first draws the image.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A per-method tally in the counting proxy

> Change `CountingProxy` in `counting_proxy.py` to keep a per-method tally in a `collections.Counter` instead of a single total.
> Confirm the tally reports `f` called twice and `g` called once.

<details>
<summary>Where to look</summary>

[Smart Reference](../../Chapters/25_Patterns--Surrogate.md#smart-reference)
wraps each forwarded call to count it.
`__getattr__()` receives the attribute name,
so use the name as the key into a `collections.Counter` in place of the single total.
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
<summary>Done when</summary>

after calling `f()`, `g()`, and `f()` through your proxy,
`print(p.calls["f"], p.calls["g"])` prints `2 1`.
Reading `p.f` twice without calling it leaves both entries where they were,
since the tally counts calls, not lookups.

<details>
<summary>Solution</summary>

`CountingProxy` with a `Counter` in place of the single total:

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

If you increment `self.calls[name]` in `__getattr__()` before the `callable()` test,
the demo still prints `2 1`, because each lookup there leads to one call.
That version counts lookups rather than calls,
so evaluating `p.f is p.f` adds two to `f`'s tally.
The solution counts inside `counted()`, so the tally advances at the call,
as it does in the chapter's `CountingProxy`.

**Tally each call by name.**
Where the chapter's `CountingProxy` keeps one total in an integer `calls`,
this one keeps a `Counter` keyed by method name.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A simple copy-on-write list

> Create a simple copy-on-write list.
> Its `share()` returns a second list over the same data and increments a reference count.
> The first `append()` through a shared list copies the data before changing it.
> Confirm that the two lists share their data before the write and hold separate copies after it.

<details>
<summary>Where to look</summary>

[Smart Reference](../../Chapters/25_Patterns--Surrogate.md#smart-reference)
shows a surrogate doing extra work around each use of an implementation.
Keep the data and a count of owners together in one small shared object,
and let `share()` hand out the same object after adding one to the count.
Have `append()` check the count and, when more than one owner exists,
copy the data into a new object first.

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
<summary>Done when</summary>

after `b = a.share()` on a list `a` holding `[1, 2, 3]`,
an `is` test shows `a` and `b` sharing one data object,
with a reference count of 2.
After `b.append(4)`,
printing both gives `[1, 2, 3] [1, 2, 3, 4]` and the same `is` test reports `False`.

<details>
<summary>Solution</summary>

`CowList` and the shared `Box` that holds its data:

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

If you build the private `Box` around `self._box.data` without the `list(...)` copy,
`b` gets a `Box` of its own that holds the same list.
`b.append(4)` then changes `a` too.
The demo prints `[1, 2, 3, 4] [1, 2, 3, 4]` while `a._box is b._box` reports `False`.
A new `Box` gives `b` its own owner count and leaves the data shared,
so the solution copies the list before the write.

**Share the data and count its owners.**
`owners` counts the `CowList`s that point at a `Box`.

**Copy before a shared write.**
`b.append(4)` decrements the shared `Box`'s count,
since `b` stops referring to that `Box`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Why the typo reports as `RecursionError`

> In `counting_proxy.py`,
> misspell `self._impl` as `self._imp` inside `__getattr__()` and run `counting_demo.py`.
> Use the fallback behavior this chapter describes to explain why the failure reports as `RecursionError` rather than an `AttributeError` naming the typo.

<details>
<summary>Where to look</summary>

[The Recursion Trap](../../Chapters/25_Patterns--Surrogate.md#the-recursion-trap)
and [Forwarding with `__getattr__()`](../../Chapters/25_Patterns--Surrogate.md#forwarding-with-getattr)
describe a method that Python calls only after normal lookup fails.
Trace what Python does when the first line inside that method reads a missing name.
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
<summary>Done when</summary>

your `exercise_4.py` catches the failure with `expected(RecursionError)` and prints `[RecursionError] maximum recursion depth exceeded`.
You can also name the attribute every nested `__getattr__()` call looks up,
and say why normal lookup never finds it.

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

`f` is missing from both the instance and `BrokenProxy`,
so Python calls `__getattr__("f")`.
That call starts by reading `self._imp`, another missing name,
so Python calls `__getattr__("_imp")`, which starts by reading `self._imp`.
Each call to `__getattr__()` starts another missing-attribute lookup,
so the calls nest until they exceed Python's recursion limit.
Python then raises a `RecursionError` before any `AttributeError` can name the typo.

The trap is specific to the fallback method.
`__getattr__()` runs only when normal lookup fails,
so any missing name it reads makes Python call `__getattr__()` again.

The chapter's working version is safe because `__init__()` assigns `self._impl`,
so normal lookup finds `_impl` on the instance and returns it.
A proxy that `copy.copy()` or `pickle` rebuilds skips `__init__()`,
so it fails the same way on its first lookup that falls through to `__getattr__()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A connection pool that hands out proxies

> Create a program similar to a DBMS that allows only a set number of connections at a time.
> Implement this with a system modeled on [*Singleton*](../../Chapters/23_Patterns--Singleton.md)
> that controls the number of "connection" objects it creates.
> When a user finishes with a connection,
> the system must check that connection back in for reuse.
> To guarantee this, return a proxy instead of a reference to the actual connection,
> and design the proxy to release the connection back to the system.

<details>
<summary>Where to look</summary>

[Protection *Proxy*](../../Chapters/25_Patterns--Surrogate.md#protection-proxy)
shows a surrogate that controls access to an implementation.
Let only a `Pool` class create the `Connection` objects,
and have `acquire()` return a proxy that forwards through `__getattr__()`.
Make the proxy a context manager whose `__exit__()` returns the connection to the pool and drops its own reference.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from typing import Any, Final, Self
from exceptions import expect, expected

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
<summary>Done when</summary>

with a limit of two,
your program lends two connections and refuses a third with an exception,
and the free count climbs back to 1 and then 2 as each client finishes.
Using a proxy after its client finished raises an exception instead of reaching a connection the pool may have lent again.

<details>
<summary>Solution</summary>

The pool, its connections, and the proxy that `acquire()` returns:

```python
# exercise_5.py
from typing import Any, Final, Self
from exceptions import expect, expected

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
with expected(RuntimeError):
    c1.query("select 3")
#: [RuntimeError] connection already released
```

If you leave out the line in `__exit__()` that sets `_connection` to `None`,
the pool gets each connection back, but the proxy keeps its reference.
After both blocks end, `c1.query()` still answers through connection 0.
When a later `acquire()` lends that connection to another client,
both proxies query through it.
The solution clears the reference,
so a released proxy raises a `RuntimeError` instead.

**Limit who creates connections.**
`Pool` alone creates `Connection` objects, all of them in its constructor.
`Pool` controls creation as a *Singleton* class does,
with the limit set at `POOL_SIZE` objects instead of one.

**Hand out a stand-in.**
The `ConnectionProxy` that `acquire()` returns forwards `query()` through `__getattr__()` and adds one action of its own:
returning that connection to the pool.
[*Singleton*](../../Chapters/23_Patterns--Singleton.md)'s exercise 2 builds [the same pool](../23_Patterns--Singleton/README.md#a-pool-of-connections-instead-of-one-instance)
without a proxy, so each caller there must remember to call `release()`.
Here the proxy takes over that step.

**Return the connection on exit.**
The proxy is also a [context manager](../../Chapters/15_Techniques--Context_Managers.md).
`__exit__()` runs whether the block ends normally or raises an exception,
so "must check that connection back in" becomes a guarantee.

**Refuse use after release.**
`__exit__()` also drops the proxy's reference to the connection,
which the pool may lend to someone else.
The check in `__getattr__()` then raises a `RuntimeError` on any later use of the proxy,
so each connection serves one client at a time.

`ConnectionProxy` is a protection proxy and a smart reference at once.
It controls access, and it adds an action (the check-in)
around each loan of the connection.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Forwarding `__len__()` explicitly

> `len(p)` raises a `TypeError` on the `Proxy` that `dunder_bypass.py` imports from `proxy_getattr.py`.
> Give that `Proxy` a `__len__()` that forwards to the implementation,
> and confirm `len(p)` returns 2.
> Then explain why `__getattr__()` could not have supplied it.

<details>
<summary>Where to look</summary>

[Special Methods Bypass `__getattr__()`](../../Chapters/25_Patterns--Surrogate.md#special-methods-bypass-getattr)
explains why `len(p)` fails on a proxy that forwards through `__getattr__()` alone.
Define `__len__()` on the proxy class and have it call `len()` on the implementation.
For the explanation, consider where `len()` looks for `__len__()`.

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
<summary>Done when</summary>

your `exercise_6.py` prints `2` for `len(p)` and `uv run ty check` passes on it.
If you delete the proxy's `__len__()`,
the checker reports `invalid-argument-type` on `len(p)`.
You can also say where `len()` looks for `__len__()` and why that lookup skips `__getattr__()`.

<details>
<summary>Solution</summary>

If `Proxy` forwards through `__getattr__()` alone, `p.__len__()` returns 2,
but `len(p)` raises a `TypeError`: `object of type 'Proxy' has no len()`.
The type checker reports the call as `invalid-argument-type`,
since `Proxy` does not match `Sized`.
The solution defines `__len__()` on the class, where `len()` looks for it.

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

`__getattr__()` could not have supplied `__len__()`,
because `len()` looks up `__len__()` on `type(p)` and calls what it finds there.
That lookup bypasses the instance, and with it `__getattr__()`,
which Python calls after a failed lookup on the instance.
Python's operators and built-in functions look up an implicitly invoked special method this way,
so the method must exist on the proxy's class.

**Define the special method on the proxy.**
`__len__()` here delegates with `len(self.__implementation)` rather than `self.__implementation.__len__()`.
Both give the same answer.
`len()` reads better.

To forward many dunders, you write one forwarding method per dunder,
or generate the methods in a loop over a list of names and assign them onto the class.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. A `change_to()` that refuses a narrower implementation

> Extend `Surrogate` in `state_surrogate.py` so `change_to()` rejects an implementation missing a method the current one has,
> and explain why the type checker could not have reported that swap.

<details>
<summary>Where to look</summary>

[*State*](../../Chapters/25_Patterns--Surrogate.md#state)
swaps the implementation behind a surrogate with `change_to()`.
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
<summary>Done when</summary>

swapping to an implementation that lacks one of the current one's methods raises a `TypeError` naming that method,
a call afterward still reaches the old implementation,
and the chapter's `test_state.py` still passes against your `Surrogate`.
You can also name the type the checker sees for both implementations.

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

**List the reachable methods.**
`methods()` reports the public callables an object carries,
the set a caller can reach through the surrogate's `__getattr__()`.

**Refuse a narrower replacement.**
`change_to()` compares the two sets and refuses the swap when the replacement drops a name the current implementation answers.

The type checker cannot make this decision.
To make it, the checker would compare the type of the implementation the surrogate holds with the type of `new`.
The checker sees `Any` for both, so to the checker each one has every method.
`Any` is the choice `state_surrogate.py` makes so that one surrogate accepts any implementation.

Annotating the stored implementation and `new` against a `Protocol` gives a different guarantee:
one shape that every implementation must meet.
A `Protocol` cannot express "at least what the last implementation had,"
because that comparison relates two runtime values rather than two declarations.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
