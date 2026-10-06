# Context Managers: Solutions

## 1. Nesting a second `Trace` inside the first

> In `trace_cm.py`, nest a second `with Trace("B") as u:` block inside the body of the first `with Trace("A") as t:` block,
> with its own `print(f"inside {u.name}")`.
> Before running it, predict the order in which the six "enter"/"inside"/"exit" lines appear.

<details>
<summary>Where to look</summary>

[The Protocol](../../Chapters/15_Techniques--Context_Managers.md#the-protocol) shows `__enter__()` running when the `with` begins and `__exit__()` when its body ends.
A second `with` inside the body is a complete enter-and-exit pair that sits within the first.
Write out the six lines by following which block must finish before the other can.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Self

class Trace:
    def __init__(self, name: str) -> None:
        ...

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: object, tb: object) -> None:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from typing import Self

class Trace:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Self:
        print(f"enter {self.name}")
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: object, tb: object) -> None:
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
Managers](../../Chapters/15_Techniques--Context_Managers.md#combining-context-managers) shows for `tag("ul")` and
`tag("li")` written on one `with` line. The order is the same whether
you write the nesting as two separate `with` statements or as one
comma-separated line.

</details>
</details>
</details>

## 2. Suppressing a second exception type

> In `demo_exceptions.py`,
> change `expected(ZeroDivisionError)` to `expected((ZeroDivisionError, TypeError))`,
> then raise a `TypeError` instead of dividing by zero,
> and confirm that `expected` catches and prints it too.

<details>
<summary>Where to look</summary>

In [The `expected` Manager](../../Chapters/15_Techniques--Context_Managers.md#the-expected-manager), `__exit__()` decides what to suppress by testing the exception type against the manager's `types` argument.
Look at which kinds of value `issubclass()` accepts as its second argument.
Then pass a tuple of classes at the call site and watch for the extra pair of parentheses.

<details>
<summary>Solution</summary>

If you write `expected(ZeroDivisionError, TypeError)` without the
inner parentheses, the script stops before printing `before`, with a
`TypeError` saying that `expected.__init__()` takes from 1 to 2
positional arguments but 3 were given. Python makes that call before
the `with` statement enters the manager, so no `__exit__()` runs to
suppress the error, and `ty` flags the call as
`too-many-positional-arguments`. The solution wraps the two classes
in a tuple, so `expected` receives one `types` argument, a shape that
`issubclass()` accepts.

```python
# ch15_expected_types.py
from exceptions import expected

with expected((ZeroDivisionError, TypeError)):
    print("before")
    raise TypeError("not a number")
#: before
#: [TypeError] not a number
print("survived")
#: survived

with expected((ZeroDivisionError, TypeError)):
    print("before")
    1 / 0
#: before
#: [ZeroDivisionError] division by zero
print("survived")
#: survived
```

**Widen what the manager catches.** You make every change the exercise asks for at the call site. `expected`
takes one `types` argument that is either an exception class or a
tuple of them, and `issubclass(exc_type, self.types)` accepts either
shape. Passing `(ZeroDivisionError, TypeError)` therefore suppresses
both, and the `TypeError` block prints a `[Type] message` line in the
same form the `ZeroDivisionError` block printed before the change.

**Check that the original type still matches.** The second block shows that the tuple still covers the original
exception.

Note the double parentheses. `expected((ZeroDivisionError, TypeError))`
passes one argument, a tuple. `expected(ZeroDivisionError, TypeError)`
passes two, and Python raises a `TypeError` at the call, since
`expected` declares a single parameter. A version taking `*types`
accepts the second form, and that is the design
`contextlib.suppress` chose.

</details>
</details>

## 3. A third manager on one `with` line

> Add a third manager to the `with` statement in `multiple.py`,
> `tag("li")` again for a second item,
> and confirm the exit order still reverses the entry order.

<details>
<summary>Where to look</summary>

[Combining Context Managers](../../Chapters/15_Techniques--Context_Managers.md#combining-context-managers) shows several managers on one `with` statement, entered left to right.
Add another `tag("li")` with its own `as` name to the managers on the `with` line, grouping them in parentheses once they outgrow one line.
Predict the closing tags before you run it, using the same last-in-first-out rule.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    ...
```

<details>
<summary>Solution</summary>

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
again) and exit in reverse order, regardless of how many managers
appear on the line.

</details>
</details>
</details>

## 4. Both pool connections leased at once

> In `test_object_pool.py`, add a test that leases both connections at once,
> entering a second `with pool.lease()` block inside the first,
> and confirms `pool.available()` reaches `0`.

<details>
<summary>Where to look</summary>

[Testing the Lease](../../Chapters/15_Techniques--Context_Managers.md#testing-the-lease) shows a test that leases a connection with `pool.lease()` and checks `pool.available()`.
Nest a second `with pool.lease()` inside the first and assert on `available()` while the test holds both connections.
Check the count again after both blocks exit.

<details>
<summary>Solution</summary>

```python
# test_ch15_both_leased.py
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

def test_both_leased_at_once() -> None:
    pool = Pool(Connection(1), Connection(2))
    with pool.lease() as first:
        with pool.lease() as second:
            assert second is not first
            assert pool.available() == 0
    assert pool.available() == 2
```

The solutions tree cannot import the chapter's `object_pool.py`, so
the file carries its own copy of `Connection` and `Pool`. In the
chapter's `test_object_pool.py` you add the test function alone.

**Hold both connections at once.** The first `lease()` takes one connection out of the queue, and the
nested second `lease()` takes the other, so `pool.available()` is `0`
inside the inner `with`. The `0` confirms the pool has no
built-in limit of "one lease at a time." The pool holds the items you
gave its constructor, and it hands out as many concurrent leases as
it has items. A third nested `lease()` would block forever in
`get()`, since this one thread holds both connections and nothing can
return one.

**Check that both connections come back.** Exiting the inner `with` puts `second`
back, then exiting the outer `with` puts `first` back,
restoring `pool.available()` to `2`.

</details>
</details>

## 5. Two `banner` decorators stacked on one function

> Stack `@banner("outer")` and `@banner("inner")` from `context_decorator.py` on a single function and predict the order of the four bracketing lines before running it.

<details>
<summary>Where to look</summary>

[Context Manager as Decorator](../../Chapters/15_Techniques--Context_Managers.md#context-manager-as-decorator) shows a `@contextmanager` generator used as a decorator through `ContextDecorator`.
Stacked decorators apply from the one nearest the `def` outward, so work out which manager wraps which.
Each call of the function then enters the managers in the order of the wrapping.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Iterator[None]:
    ...

@banner("outer")
@banner("inner")
def report() -> None:
    ...
```

<details>
<summary>Solution</summary>

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

**Apply the decorators bottom-up.** The prediction is the same one stacking produces anywhere. Python reads
the stack as `report = banner("outer")(banner("inner")(report))`.
`@banner("inner")` is nearest the `def`, so it wraps `report()` first,
and `@banner("outer")` then wraps the inner wrapper. Calling `report()`
therefore enters the outer manager, which calls the inner wrapper,
which enters the inner manager before running the body. Unwinding
reverses that order, so the four bracketing lines nest rather than
interleave.

**Enter a fresh manager on each call.** Each `@banner(...)` line builds one manager object, when Python
defines `report()`. A generator manager is single-use, so the wrapper
that `ContextDecorator` supplies does not enter that object. On each
call of `report()` the wrapper builds a fresh manager from the same generator
function and arguments, and enters that one. A hand-written
class-based manager decorating a function re-enters the same instance
on every call instead, so every call shares any state the instance
holds.

</details>
</details>
</details>

## 6. `ignore_missing`, which suppresses only `KeyError`

> Write a context manager `ignore_missing` whose `__exit__()` suppresses `KeyError` and lets everything else through,
> without using `contextlib.suppress`.
> Test it with a block that raises a `KeyError` and a block that raises a `ValueError`.

<details>
<summary>Where to look</summary>

[The `__exit__()` Arguments](../../Chapters/15_Techniques--Context_Managers.md#the-__exit__-arguments) shows that a true return value from `__exit__()` suppresses the exception and a false one lets it continue.
Write a class whose `__exit__()` returns the result of testing `exc_type` against `KeyError`.
`exc_type` is `None` when the block finishes cleanly.
Test the `ValueError` case inside the chapter's `expected()` so it catches and prints the exception.

<details>
<summary>The shape</summary>

```python
# The shape of ignore_missing.py
from types import TracebackType
from exceptions import expected

class ignore_missing:
    def __enter__(self) -> None:
        ...

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: TracebackType | None,
    ) -> bool:
        ...
```

<details>
<summary>Solution</summary>

If you return `issubclass(exc_type, KeyError)` without the `None` test,
the demo prints the same two lines, because both of its blocks raise an exception.
A block that finishes cleanly then fails.
`__exit__()` receives `None`, and `issubclass()` raises a `TypeError`.
`ty` reports an `invalid-argument-type` at the `issubclass()` call,
so the type checker catches the mistake the demo misses.
The solution tests `exc_type is not None` first.

```python
# ignore_missing.py
from types import TracebackType
from exceptions import expected

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

with expected(ValueError):
    with ignore_missing():
        raise ValueError("not a lookup problem")
#: [ValueError] not a lookup problem
```

**Suppress one exception type.** `__exit__()` decides an exception's fate through its return value:
truthy suppresses, falsy lets the exception continue. Returning
`issubclass(exc_type, KeyError)` therefore suppresses `KeyError` and
propagates everything else.

**Check that other exceptions propagate.** The second block confirms the
propagation. The `ValueError` passes through `ignore_missing` and
reaches the chapter's `expected`, which prints it.

**Handle a clean exit.** The `exc_type is not None` test keeps the normal path working. When a
block finishes without an exception, Python still calls `__exit__()`,
passing `None` for all three arguments, and
`issubclass(None, KeyError)` raises a `TypeError`. Checking for `None`
first also lets the type checker narrow `exc_type` to
`type[BaseException]`, the type `issubclass()` requires.

The class uses a lowercase name because you use it like a function.
`contextlib.suppress` is lowercase for the same reason.

</details>
</details>
</details>

## 7. `exit_stack.py` driven from the command line

> Rewrite `exit_stack.py` to take its names from `sys.argv[1:]`,
> run it with no arguments and with three,
> and confirm the close order reverses the open order in both cases.

<details>
<summary>Where to look</summary>

[Combining Context Managers](../../Chapters/15_Techniques--Context_Managers.md#combining-context-managers) shows `ExitStack` entering a number of managers that the code decides at runtime.
Build the list of names from `sys.argv[1:]` and pass it to the function that calls `enter_context()` for each one.
Run it with no names and with three, and compare the close order with the open order.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    ...

def wrap(names: list[str]) -> None:
    ...
```

<details>
<summary>Solution</summary>

Both calls to `wrap()` go, replaced by one call that reads the names
from the command line:

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

**Close in reverse order of opening.** `enter_context()` pushes each manager onto the stack as the
comprehension walks the list left to right. Leaving the `with` unwinds
that stack, so the closes come out in reverse. The reversal holds for
any number of names, including zero, the property the exercise asks
you to confirm.

The empty run is the more interesting one. Nothing opens, so nothing
closes, and `with ExitStack() as stack:` still enters and exits
correctly around a body whose stack stays empty. That degenerate case
shows why `ExitStack` exists. A fixed `with a, b, c:` line settles its
count in the source. `ExitStack` accepts a count settled only at
runtime, zero included, and a command line is one source of
such a count.

The `sys.argv` rewrite stays out of the extracted listings, because
the book's output checker runs each listing with `exec()` inside a
checker process, and a script reading `sys.argv` sees the checker's
arguments instead. The listing below passes the names to `wrap()`
as list literals, so the checker can run it, and it shows both cases:

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

</details>
</details>
</details>

## 8. `careless()` with its `try`/`finally` restored

> Wrap the `yield` in `careless()` from `no_finally.py` in `try`/`finally`,
> with the `exit` line in the `finally`.
> Before running it, predict where `exit A` appears relative to `caught: boom`.

<details>
<summary>Where to look</summary>

[A Basic Context Manager](../../Chapters/15_Techniques--Context_Managers.md#a-basic-context-manager) shows that a `@contextmanager` generator needs `try`/`finally` around its `yield` to clean up after an exception.
The `with` statement throws the block's exception into the generator at the `yield`.
Decide whether the `finally` body runs before or after the `except` clause outside the `with`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def careful(name: str) -> Iterator[str]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def careful(name: str) -> Iterator[str]:
    print(f"enter {name}")
    try:
        yield name
    finally:
        print(f"exit {name}")

try:
    with careful("A"):
        raise ValueError("boom")
except ValueError as error:
    print("caught:", error)
#: enter A
#: exit A
#: caught: boom
```

**Clean up before the exception propagates.** `exit A` now prints, and it prints before `caught: boom`. Python
raises the block's `ValueError` inside the generator, at the `yield`.
The `finally` runs as the exception leaves the generator, and only
then does the exception leave the `with` statement and reach the
`except`.
That is the order `exit_on_error.py` shows for the class form: cleanup
first, then propagation.

In `no_finally.py` the same exception leaves the generator from the
bare `yield`, so the `print()` after it does not run. The `finally` is
the only difference between the two listings, apart from the
function's name.

</details>
</details>
</details>
