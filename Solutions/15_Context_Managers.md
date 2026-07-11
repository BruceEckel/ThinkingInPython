# Context Managers: Solutions

## 1. Nesting a second `Trace` inside the first

```python
# exercise_1.py
from typing import Self

class Trace:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Self:
        print(f"enter {self.name}")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        print(f"exit {self.name}")

with Trace("A") as t:
    print(f"inside {t.name}")
    with Trace("B") as u:
        print(f"inside {u.name}")
#: enter A
#: inside A
#: enter B
#: inside B
#: exit B
#: exit A
```

Entering is outside-in (`A` then `B`), and exiting is inside-out (`B`
then `A`). `B`'s whole lifetime, enter and exit, sits nested inside
`A`'s, the same last-in-first-out order [Combining Context
Managers](#combining-context-managers) shows for `tag("ul")` and
`tag("li")` written on one `with` line. Writing the nesting as two
separate `with` statements instead of one comma-separated line makes
no difference to the order.

## 2. Suppressing a second exception type

```python
# exercise_2.py
class Ignore:
    def __init__(self, *types) -> None:
        self.types = types

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb) -> bool:
        return (exc_type is not None
                and issubclass(exc_type, self.types))

with Ignore(ZeroDivisionError, TypeError):
    print("before")
    raise TypeError("boom")
print("survived")
#: before
#: survived
```

`Ignore.__init__` already collects every type you pass it into the
`self.types` tuple through `*types`, so adding `TypeError` needed no
change to the class itself, only to the call site. `issubclass(exc_type,
self.types)` accepts a tuple of types and returns `True` if `exc_type`
matches any of them, so `TypeError` is now suppressed exactly like
`ZeroDivisionError` was.

## 3. A fourth manager on one `with` line

```python
# exercise_3.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

with tag("ul") as outer, tag("li") as inner1, tag("li") as inner2:
    print(f"  {outer} then {inner1} then {inner2}")
#: <ul>
#: <li>
#: <li>
#:   ul then li then li
#: </li>
#: </li>
#: </ul>
```

All three managers enter left to right (`ul`, then `li`, then `li`
again) and exit in the exact reverse order, regardless of how many
managers appear on the line. The pattern from two managers extends
unchanged to three, four, or more.

## 4. Both pool connections leased at once

```python
# exercise_4.py
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Queue

@dataclass(frozen=True)
class Connection:
    number: int

class Pool[R]:
    def __init__(self, *items: R) -> None:
        self._available: Queue[R] = Queue()
        for item in items:
            self._available.put(item)

    @contextmanager
    def lease(self) -> Iterator[R]:
        item = self._available.get()
        try:
            yield item
        finally:
            self._available.put(item)

    def available(self) -> int:
        return self._available.qsize()

pool = Pool(Connection(1), Connection(2))
with pool.lease() as c1:
    with pool.lease() as c2:
        print("available while both leased:", pool.available())
print("available after both returned:", pool.available())
#: available while both leased: 0
#: available after both returned: 2
```

The first `lease()` takes one connection out of the queue, and the
nested second `lease()` takes the other, so `pool.available()` reports
`0` while both are checked out. Exiting the inner `with` returns its
connection first, then exiting the outer `with` returns the second,
restoring `pool.available()` to `2`. This confirms the pool has no
built-in limit of "one lease at a time"; it only has as many items as
you gave it in the constructor, and it happily hands out however many
distinct leases there are connections for.
