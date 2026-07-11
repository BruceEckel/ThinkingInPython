# Singleton: Solutions

## 1. `singleton_eager.py` rewritten to lazy initialization

```python
# exercise_1.py
from dataclasses import dataclass, field
from typing import Any, ClassVar

class OnlyOne:
    @dataclass
    class __OnlyOne:
        val: list[str] = field(default_factory=list)

    instance: ClassVar[Any] = None  # Nothing built yet

    def __init__(self, arg: str) -> None:
        if OnlyOne.instance is None:
            # Built on first use:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        OnlyOne.instance.val.append(arg)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

x = OnlyOne("sausage")
y = OnlyOne("eggs")
print(x.val, x is y, x.instance is y.instance)
#: ['sausage', 'eggs'] False True
```

This is `singleton_pattern.py` itself: the change from eager to lazy
is exactly reintroducing the `None` sentinel and the `if
OnlyOne.instance is None:` guard that the eager version removed. Both
versions produce identical externally-visible behavior, `x.val`
accumulates the same way, `x is y` is still `False`, and
`x.instance is y.instance` is still `True`. The only difference is
*when* the shared inner object comes into existence: at the first
`OnlyOne(...)` call for the lazy version, versus at class-definition
time (module import) for the eager one. Comparing the two files
side by side shows that "lazy vs. eager" is a small, local decision
that does not otherwise change how callers use the class.

## 2. A pool of connections instead of one instance

```python
# exercise_2.py
from dataclasses import dataclass
from functools import cache

@dataclass(frozen=True)
class Connection:
    number: int

class ConnectionPool:
    def __init__(self, size: int) -> None:
        self._all = [Connection(i) for i in range(size)]
        self._available = list(self._all)
        self._leased: set[Connection] = set()

    def acquire(self) -> Connection:
        if not self._available:
            raise RuntimeError("pool exhausted")
        conn = self._available.pop()
        self._leased.add(conn)
        return conn

    def release(self, conn: Connection) -> None:
        self._leased.discard(conn)
        self._available.append(conn)

@cache
def pool() -> ConnectionPool:
    "Always returns the same ConnectionPool instance."
    return ConnectionPool(size=2)

p1 = pool()
p2 = pool()
print(p1 is p2)
#: True
c1 = p1.acquire()
c2 = p1.acquire()
print(c1 != c2)
#: True
try:
    p1.acquire()
except RuntimeError as e:
    print("caught:", e)
#: caught: pool exhausted
p1.release(c1)
c3 = p1.acquire()
print(c3 == c1)
#: True
```

`@cache` on the zero-argument `pool()` constructor function still
guarantees exactly one `ConnectionPool` object exists (`p1 is p2`),
the same trick `cached_factory_singleton.py` uses for `Settings`. The
change is what that one object *is*: instead of holding a single
value, it holds a fixed collection of `Connection`s and tracks which
are checked out. `acquire()` and `release()` replace the "get the
instance" idea with "borrow one member of a pool and give it back,"
similar in spirit to [Context Managers](15_Context_Managers.md#an-object-pool)'s
`Pool.lease()`, but without the automatic return a context manager
guarantees; here a caller must remember to call `release()`.

## 3. A class-based singleton rewritten as a module

```python
# only_one.py
val: list[str] = []

def add(arg: str) -> None:
    val.append(arg)
```

```python
# use_only_one.py
import only_one

only_one.add("sausage")
only_one.add("eggs")
print(only_one.val)
#: ['sausage', 'eggs']
```

This behaves exactly like `OnlyOne` from `singleton_pattern.py`: a
shared, one-and-only-one `val` list, appended to from anywhere in the
program. There is no wrapper class, no nested private class, no
`ClassVar` sentinel, and no `__getattr__()` delegation, because the
module itself is already the single shared object Python caches in
`sys.modules`.

For real code, prefer the module. It is less code, has no indirection
to read through, and gets the same guarantee for free, the same
argument [A Module Is Already a Singleton](#a-module-is-already-a-singleton)
makes at the top of the chapter. The class-based versions only earn
their complexity when something genuinely needs the shape of a class,
such as participating in an interface other code expects, or needing
`__new__()`-level control over construction; absent that requirement,
a module is the simpler tool that already does the job.
