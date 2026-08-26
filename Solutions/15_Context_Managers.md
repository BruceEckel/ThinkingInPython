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
Managers](../Chapters/15_Context_Managers.md#combining-context-managers) shows for `tag("ul")` and
`tag("li")` written on one `with` line. Writing the nesting as two
separate `with` statements instead of one comma-separated line makes
no difference to the order.

## 2. Suppressing a second exception type

```python
# ch15_ignore_types.py

class ignore:
    def __init__(self, types: type[BaseException] |
                 tuple[type[BaseException], ...]) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if (exc_type is None
            or not issubclass(exc_type, self.types)):
            return False
        print(f"{exc!r}")
        return True

with ignore((ZeroDivisionError, TypeError)):
    print("before")
    raise TypeError("not a number")
print("survived")
#: before
#: TypeError('not a number')
#: survived

with ignore((ZeroDivisionError, TypeError)):
    print("before")
    1 / 0
print("survived")
#: before
#: ZeroDivisionError('division by zero')
#: survived
```

The class is the chapter's `ignore` with the `ALL` default left out,
since the exercise never calls it with no argument. Everything the
exercise asks for happens at the call site: `ignore` takes one `types`
argument that is either an exception class or a tuple of them, and
`issubclass(exc_type, self.types)` accepts either shape. Passing
`(ZeroDivisionError, TypeError)` therefore suppresses both, and the
`TypeError` block prints the same `repr()` line the `ZeroDivisionError`
block printed before the change.

Note the double parentheses. `ignore((ZeroDivisionError, TypeError))`
passes one argument, a tuple. `ignore(ZeroDivisionError, TypeError)`
passes two, which is a `TypeError` at the call itself, since `ignore`
declares a single parameter. A version taking `*types` would accept the
second spelling, and that is the design `contextlib.suppress` chose.

## 3. A third manager on one `with` line

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

with (tag("ul") as outer, tag("li") as inner1,
      tag("li") as inner2):
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
        print("available while both leased:",
              pool.available())
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

## 5. Two `banner` decorators stacked on one function

```python
# exercise_5.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Iterator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

@banner("outer")
@banner("inner")
def report() -> None:
    print("quarterly numbers")

report()
#: === outer ===
#: === inner ===
#: quarterly numbers
#: === inner ends ===
#: === outer ends ===
```

The prediction is the same one stacking produces anywhere: this is
`report = banner("outer")(banner("inner")(report))`. `@banner("inner")`
is nearest the `def`, so it wraps `report()` first, and `@banner("outer")`
then wraps that result. Calling `report()` therefore enters the outer
manager, which calls the inner wrapper, which enters the inner manager
before running the body. Unwinding reverses it, so the four bracketing
lines nest rather than interleave.

Each decoration is one `banner(...)` object reused for every call, not
one per call. It works because `@contextmanager` returns a
`ContextDecorator`, whose `__call__()` recreates the generator on each
invocation. A hand-written class-based manager decorating a function has
to do that itself, or the second call finds a generator that is
already exhausted.

## 6. `ignore_missing`, which suppresses only `KeyError`

```python
# ignore_missing.py
from types import TracebackType

class ignore_missing:
    def __enter__(self) -> None:
        return None

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> bool:
        return (exc_type is not None
                and issubclass(exc_type, KeyError))

stock = {"apple": 3}

with ignore_missing():
    print(stock["pear"])
    print("never reached")
print("survived the KeyError")
#: survived the KeyError

try:
    with ignore_missing():
        raise ValueError("not a lookup problem")
except ValueError as e:
    print("escaped:", e)
#: escaped: not a lookup problem
```

`__exit__()` decides an exception's fate through its return value:
truthy suppresses, falsy lets the exception continue. Returning
`issubclass(exc_type, KeyError)` therefore suppresses `KeyError` and
propagates everything else, which the second block confirms by catching
the `ValueError` outside the `with`.

The `exc_type is not None` test is what keeps the normal path working.
When a block finishes without an exception, Python still calls
`__exit__()`, passing `None` for all three arguments, and
`issubclass(None, KeyError)` raises a `TypeError`. Checking for `None`
first also gives the type checker what it needs to narrow `exc_type` to
`type[BaseException]`, which is what `issubclass()` requires.

The class is named like a function because you use it like one, the
same reason `contextlib.suppress` carries a lowercase name.

## 7. `exit_stack.py` driven from the command line

The rewrite is one line. `wrap(["a", "b"])` becomes:

```python
import sys

wrap(sys.argv[1:])
```

Run with three names, `uv run python exit_stack.py x y z`:

```text
open x
open y
open z
using ['x', 'y', 'z']
close z
close y
close x
```

Run with none, `uv run python exit_stack.py`:

```text
using []
```

`enter_context()` pushes each manager onto the stack as the
comprehension walks the list left to right, and leaving the `with`
unwinds that stack, so the closes come out in reverse. The order does
not depend on how many names arrive, which is the property to confirm.

The empty run is the more interesting one. Nothing opened, so nothing
closes, and `with ExitStack() as stack:` still enters and exits
correctly around a body that manages nothing. That degenerate case is
why `ExitStack` exists: the same code covers zero managers, which a
fixed `with a, b, c:` line cannot express, and a count known only at
runtime is the situation a command line hands you.

This solution's listing is not extracted and run like the others,
because a script reading `sys.argv` produces different output under the
book's output checker, which runs every listing inside one process with
its own arguments. The version below passes the names to `wrap()`
directly, which is checkable and shows both cases:

```python
# exercise_7.py
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"open {name}")
    try:
        yield name
    finally:
        print(f"close {name}")

def wrap(names: list[str]) -> None:
    with ExitStack() as stack:
        open_tags = [stack.enter_context(tag(n))
                     for n in names]
        print("using", open_tags)

wrap([])
#: using []
wrap(["x", "y", "z"])
#: open x
#: open y
#: open z
#: using ['x', 'y', 'z']
#: close z
#: close y
#: close x
```
