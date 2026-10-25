# Context Managers: Solutions

## 1. Nesting a second `Trace` inside the first

> In `trace_cm.py`, nest a second `with Trace("C") as u:` block inside the body of the first `with Trace("A") as t:` block,
> with its own `print(f"inside {u.name}")`.
> Before running it, predict the order in which the six "enter"/"inside"/"exit" lines appear.

<details>
<summary>Where to look</summary>

[The Protocol](../../Chapters/15_Techniques--Context_Managers.md#the-protocol)
shows `__enter__()` running when the `with` begins and `__exit__()` when its body ends.
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
<summary>Done when</summary>

you wrote your six-line prediction before running,
and your edited `trace_cm.py` prints `enter C` right after `inside A` and `exit C` right before `exit A`,
the last line.
If your prediction differed, you can say which block had to finish first.

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
    with Trace("C") as u:
        print(f"inside {u.name}")
#: enter A
#: inside A
#: enter C
#: inside C
#: exit C
#: exit A
```

Entering is outside-in (`A` then `C`).
Exiting is inside-out (`C` then `A`).
`C`'s whole lifetime, enter and exit, sits nested inside `A`'s lifetime.
[Combining Context Managers](../../Chapters/15_Techniques--Context_Managers.md#combining-context-managers)
shows the same last-in-first-out order for `tag("ul")` and `tag("li")` written on one `with` line.
The order is the same whether you write the nesting as two separate `with` statements or as one comma-separated line.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

In [The `expected` Manager](../../Chapters/15_Techniques--Context_Managers.md#the-expected-manager),
`__exit__()` decides what to suppress by testing the exception type against the manager's `types` argument.
Look at which kinds of value `issubclass()` accepts as its second argument.
Then pass a tuple of classes at the call site and watch for the extra pair of parentheses.

<details>
<summary>Done when</summary>

your edited `demo_exceptions.py` prints `before`,
then a line starting `[TypeError]`, then `survived`,
and `uv run ty check` passes on it.
A block that still divides by zero under the same `expected(...)` call prints `[ZeroDivisionError] division by zero`,
so the original type stays covered.

<details>
<summary>Solution</summary>

The solution wraps the two classes in a tuple,
so `expected` receives one `types` argument:

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

**Widen what the manager catches.**
Every change the exercise requires sits at the call site.
`expected` takes one `types` argument that is either an exception class or a tuple of them,
and `issubclass(exc_type, self.types)` accepts either shape.
Passing `(ZeroDivisionError, TypeError)` therefore suppresses both.

If you write `expected(ZeroDivisionError, TypeError)` without the inner parentheses,
the script stops before printing `before`,
with a `TypeError` saying that `expected.__init__()` takes from 1 to 2 positional arguments but 3 were given.
Python makes that call before the `with` statement enters the manager,
so the `TypeError` propagates straight out of the script.
`ty` flags the call as `too-many-positional-arguments`.

`contextlib.suppress` takes its exception classes as `*exceptions`,
so it accepts them as separate arguments.
A version of `expected` taking `*types` accepts `expected(ZeroDivisionError, TypeError)` the same way.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. A third manager on one `with` line

> Add a third manager to the `with` statement in `multiple.py`,
> `tag("li")` again for a second item,
> and confirm the exit order still reverses the entry order.

<details>
<summary>Where to look</summary>

[Combining Context Managers](../../Chapters/15_Techniques--Context_Managers.md#combining-context-managers)
shows several managers on one `with` statement, entered left to right.
Add another `tag("li")` with its own `as` name to the managers on the `with` line,
grouping them in parentheses once they outgrow one line.
Predict the closing tags before you run `multiple.py`,
using the same last-in-first-out rule.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
    ...
```

<details>
<summary>Done when</summary>

your edited `multiple.py` prints `<ul>`, `<li>`,
`<li>` before the body line and `</li>`, `</li>`, `</ul>` after it,
matching the closing order you predicted before running it.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
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

The exit order reverses the entry order for any number of managers on the line.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Both pool connections leased at once

> In `test_object_pool.py`, add a test that leases both connections at once,
> entering a second `with pool.lease()` block inside the first,
> and confirms `pool.available()` reaches `0`.

<details>
<summary>Where to look</summary>

[Testing the Lease](../../Chapters/15_Techniques--Context_Managers.md#testing-the-lease)
shows a test that leases a connection with `pool.lease()` and checks `pool.available()`.
Nest a second `with pool.lease()` inside the first and assert on `available()` while the test holds both connections.
Check the count again after both blocks exit.

<details>
<summary>Done when</summary>

`uv run pytest` on your `test_object_pool.py` passes with four tests,
and your new test asserts `pool.available() == 0` inside the inner `with` and `2` after both blocks exit.
Changing the expected `0` to `1` makes that test fail.

<details>
<summary>Solution</summary>

```python
# test_ch15_both_leased.py
from collections.abc import Generator
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
    def lease(self) -> Generator[R]:
        item = self._available.get()
        try:
            yield item
        finally:
            self._available.put(item)

    def available(self) -> int:
        return self._available.qsize()

def test_both_leased_at_once() -> None:
    pool = Pool(Connection(1), Connection(2))
    with pool.lease() as first:  # [1]
        with pool.lease() as second:  # [2]
            assert second is not first
            assert pool.available() == 0
    assert pool.available() == 2
```

**Hold both connections at once.**
`pool.available() == 0` inside the `with` at `[2]` confirms that the pool hands out one concurrent lease for each item you gave its constructor.
A third nested `lease()` blocks forever in `get()`,
since the one thread that can return a connection is the thread waiting for it.

**Check that both connections come back.**
Exiting the inner `with` (`[2]`) puts `second` back,
then exiting the outer `with` (`[1]`) puts `first` back,
restoring `pool.available()` to `2`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. Two `banner` decorators stacked on one function

> Stack `@banner("outer")` and `@banner("inner")` from `context_decorator.py` on a single function and predict the order of the four bracketing lines before running it.

<details>
<summary>Where to look</summary>

[Context Manager as Decorator](../../Chapters/15_Techniques--Context_Managers.md#context-manager-as-decorator)
shows a `@contextmanager` generator used as a decorator through `ContextDecorator`.
Stacked decorators apply from the one nearest the `def` outward,
so work out which manager wraps which.
Each call of the function then enters the managers in the order of the wrapping.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Generator[None]:
    ...

@banner("outer")
@banner("inner")
def quarterly() -> None:
    ...
```

<details>
<summary>Done when</summary>

you wrote your prediction before running,
and your function prints `=== outer ===` first and `=== outer ends ===` last,
with the two `inner` lines nested inside them around the body line.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Generator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

@banner("outer")
@banner("inner")
def quarterly() -> None:
    print("quarterly numbers")

quarterly()
#: === outer ===
#: === inner ===
#: quarterly numbers
#: === inner ends ===
#: === outer ends ===
```

**Apply the decorators bottom-up.**
Stacked context-manager decorators apply in the same order as any other stacked decorators.
Python evaluates the stack as `quarterly = banner("outer")(banner("inner")(quarterly))`.
`@banner("inner")` is nearest the `def`, so it wraps `quarterly()` first,
and `@banner("outer")` then wraps the inner wrapper.
Calling `quarterly()` therefore enters the outer manager first.
Inside the outer manager, the outer wrapper calls the inner wrapper,
which enters the inner manager and then runs the body.
Unwinding reverses that order,
so the four bracketing lines nest rather than interleave.

**Enter a fresh manager on each call.**
When Python defines `quarterly()`,
each `@banner(...)` line builds one manager object.
A generator manager is single-use,
so the wrapper that `ContextDecorator` supplies reads that object's generator function and arguments.
On each call of `quarterly()` the wrapper builds a fresh manager from them and enters the fresh one.
A hand-written class-form manager decorating a function re-enters the same instance on every call,
so every call shares any state the instance holds.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. `ignore_missing`, which suppresses only `KeyError`

> Write a context manager `ignore_missing` whose `__exit__()` suppresses `KeyError` and lets everything else through,
> without using `contextlib.suppress`.
> Test it with a block that raises a `KeyError` and a block that raises a `ValueError`.

<details>
<summary>Where to look</summary>

[The `__exit__()` Arguments](../../Chapters/15_Techniques--Context_Managers.md#the-__exit__-arguments)
shows that a true return value from `__exit__()` suppresses the exception and a false one lets it continue.
Write a class whose `__exit__()` returns the result of testing `exc_type` against `KeyError`.
`exc_type` is `None` when the block finishes cleanly.
Test the `ValueError` case inside the chapter's `expected()` so `expected()` catches and prints the exception.

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
<summary>Done when</summary>

your `KeyError` block lets the line after the `with` print,
and your `ValueError` block, wrapped in the chapter's `expected()`,
prints `[ValueError]` with your message.
A third `with ignore_missing():` block that finishes cleanly runs without an exception,
and `uv run ty check` passes on your file.

<details>
<summary>Solution</summary>

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

**Suppress one exception type.**
The return value of `__exit__()` determines whether the exception continues.
A truthy value suppresses the exception.
A falsy value lets it continue.
Returning `issubclass(exc_type, KeyError)` therefore suppresses `KeyError` and lets every other exception propagate.

**Handle a clean exit.**
The `exc_type is not None` test keeps the normal path working.
When a block finishes cleanly,
Python still calls `__exit__()` and passes `None` for all three arguments.
Without the test, a clean exit calls `issubclass(None, KeyError)`,
which raises a `TypeError`.
Checking for `None` first also lets the type checker narrow `exc_type` to `type[BaseException]`,
as `issubclass()` requires.

If you return `issubclass(exc_type, KeyError)` without the `None` test,
the demo prints the same two lines,
because both of its blocks raise an exception.
In that version a block that finishes cleanly raises a `TypeError` from the `issubclass()` call.
`ty` reports an `invalid-argument-type` at the `issubclass()` call,
so the type checker catches the mistake that the demo's output hides.

The class uses a lowercase name because you use it like a function.
`contextlib.suppress` is lowercase for the same reason.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. `exit_stack.py` driven from the command line

> Rewrite `exit_stack.py` to take its names from `sys.argv[1:]`,
> run it with no arguments and with three,
> and confirm that with three names the close order reverses the open order,
> and that with none the program prints `using []` alone.

<details>
<summary>Where to look</summary>

[Combining Context Managers](../../Chapters/15_Techniques--Context_Managers.md#combining-context-managers)
shows `ExitStack` entering a number of managers that the code decides at runtime.
Build the list of names from `sys.argv[1:]` and pass it to the function that calls `enter_context()` for each one.
Run `exit_stack.py` with no names and with three,
and compare the close order with the open order.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from collections.abc import Generator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
    ...

def wrap(names: list[str]) -> None:
    ...
```

<details>
<summary>Done when</summary>

`uv run python exit_stack.py x y z` prints `<x>`, `<y>`, `<z>`,
the `using` line, then `</z>`, `</y>`, `</x>`,
and `uv run python exit_stack.py` prints `using []` as its one line.

<details>
<summary>Solution</summary>

One call that reads the names from the command line replaces both calls to `wrap()`:

```python
import sys

wrap(sys.argv[1:])
```

Run with three names, `uv run python exit_stack.py x y z`:

```text
<x>
<y>
<z>
using ['x', 'y', 'z']
</z>
</y>
</x>
```

Run with none, `uv run python exit_stack.py`:

```text
using []
```

**Close in reverse order of opening.**
`enter_context()` pushes each manager onto the stack as the comprehension iterates over the list left to right.
Leaving the `with` unwinds that stack, so the closing tags print in reverse.
The reversal holds for any number of names.

In the empty run, `with ExitStack() as stack:` still enters and exits around a body whose stack stays empty.

The empty run shows why `ExitStack` exists.
A written-out `with a, b, c:` line settles its count in the source.
`ExitStack` accepts a count settled at runtime,
such as the number of names on a command line, zero included.

The `sys.argv` rewrite stays out of the extracted listings.
The book's output checker runs each listing with `exec()` inside the checker's own process,
so a script reading `sys.argv` gets the checker's arguments instead.
Here, `exercise_7.py` passes the names to `wrap()` as list literals,
so the checker can run both cases:

```python
# exercise_7.py
from collections.abc import Generator
from contextlib import ExitStack, contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

def wrap(names: list[str]) -> None:
    with ExitStack() as stack:
        open_tags = [stack.enter_context(tag(n))
                     for n in names]
        print("using", open_tags)

wrap([])
#: using []
wrap(["x", "y", "z"])
#: <x>
#: <y>
#: <z>
#: using ['x', 'y', 'z']
#: </z>
#: </y>
#: </x>
```

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. `careless()` with its `try`/`finally` restored

> Wrap the `yield` in `careless()` from `no_finally.py` in `try`/`finally`,
> with the `exit` line in the `finally`.
> Before running it, predict where `exit A` appears relative to `caught: boom`.

<details>
<summary>Where to look</summary>

[A Basic Context Manager](../../Chapters/15_Techniques--Context_Managers.md#a-basic-context-manager)
shows that a `@contextmanager` generator needs `try`/`finally` around its `yield` to clean up after an exception.
The `with` statement throws the block's exception into the generator at the `yield`.
Decide whether the `finally` body runs before or after the `except` clause outside the `with`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def careful(name: str) -> Generator[str]:
    ...
```

<details>
<summary>Done when</summary>

you wrote your prediction before running,
and your edited generator prints `enter A`, `exit A`,
`caught: boom` in that order,
so `exit A` now appears and comes before `caught: boom`.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def careful(name: str) -> Generator[str]:
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

**Clean up before the exception propagates.**
Python raises the block's `ValueError` inside the generator, at the `yield`.
The `finally` runs as the exception propagates out of the generator,
and only then does the exception propagate out of the `with` statement to the `except`.
That is the order `exit_on_error.py` shows for the class form: cleanup first,
then propagation.

In `no_finally.py` the same exception propagates out of the generator at a `yield` with no `try` around it,
so the `print()` after the `yield` does not run.
Apart from the function's name,
the `finally` is the one difference between the two listings.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
