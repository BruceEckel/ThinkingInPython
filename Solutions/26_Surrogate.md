# Surrogate: Solutions

## 1. A virtual proxy: lazy creation of an expensive object

```python
# exercise_1.py
from typing import Any

class ExpensiveResource:
    def __init__(self) -> None:
        print("creating ExpensiveResource (slow!)")
        self.data = [1, 2, 3]

    def query(self) -> list:
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
triggers `__getattr__()`, not when `LazyProxy()` is constructed. Every
attribute access checks `self._real` and builds the real object on the
first one that finds it missing; every later access reuses the same
instance. This is the same `__getattr__()` delegation `proxy_2.py` and
`counting_proxy.py` already use, just guarding the moment of creation
instead of forwarding to an object that already exists.

## 2. A smart reference: counting method calls

`counting_proxy.py`, already shown in this chapter, is exactly this
exercise:

```python
# exercise_2.py
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
#: f()
#: g()
#: f()
#: calls: 3
```

Every method access through the proxy returns a wrapped callable that
increments `self.calls` before forwarding to the real method, so
`p.calls` tracks exactly how many method calls have passed through
`p`, regardless of which method was called. A non-callable attribute
passes straight through, uncounted, which is what
`test_proxy_counts_only_calls()` in the chapter already checks.

## 3. A simple copy-on-write list

```python
# exercise_3.py
from __future__ import annotations

class Box:
    def __init__(self, data: list) -> None:
        self.data = data
        self.owners = 1

class CowList:
    def __init__(self, data: list | None = None,
                 _box: Box | None = None) -> None:
        self._box = (
            _box if _box is not None else Box(list(data or [])))

    def share(self) -> CowList:
        self._box.owners += 1
        return CowList(_box=self._box)  # Shares the same Box, for now

    def append(self, item: object) -> None:
        if self._box.owners > 1:
            # Someone else shares this Box: copy before mutating
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
`owners` tracking how many `CowList`s point at it. `share()` looks free
because it copies nothing, just a reference and a bumped count. The
copy only happens inside `append()`, and only when `owners > 1`: `b`
detaches into its own private `Box` holding a fresh copy of the data,
decrements the shared `Box`'s count back down (since `b` is no longer
one of its owners), and then appends to its own copy. `a`, which never
mutated, still points at the original, untouched `Box`. The cost of
copying is deferred until the moment a write actually happens, and
paid only by the list that writes, exactly what "copy-on-write" means.
