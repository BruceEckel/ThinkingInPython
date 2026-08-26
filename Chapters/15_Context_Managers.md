# Context Managers

The `with` statement,
introduced in [Control Flow](04_Control_Flow.md#context-managers),
marks out a span of execution:
it runs setup before a block and cleanup after it,
even if the block raises an exception.
That is far more reliable than the `__del__()` approach in [Cleanup](10_Cleanup.md).
This chapter shows how to write your own context managers, and how `with` works.

The payoff is a borrower's contract two lines long:

```python
with pool.lease() as conn:
    conn.query("SELECT name FROM users")
```

The connection returns to the pool on every path out of that block,
including the exception path, and the borrower writes nothing to arrange it.
[An Object Pool](#an-object-pool) builds it.

## A Basic Context Manager

The simplest way to write a context manager is a generator function with a single `yield`,
which the `contextlib.contextmanager` decorator turns into a context manager.
The `yield` here works the way it does in a `pytest` fixture that [`yield`s its value](11_Testing.md#fixtures-replace-setup-and-teardown):
everything before it is setup, everything after it is teardown.
[Iterators](23_Iterators.md#generators) covers generators in full;
this chapter needs nothing beyond that shape.

```python
# trace_gen.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def trace(name: str) -> Iterator[str]:
    print(f"enter {name}")  # Setup
    try:
        yield name  # The block runs here
    finally:
        print(f"exit {name}")  # Cleanup

if __name__ == "__main__":
    with trace("A") as t:
        print(f"inside {t}")
#: enter A
#: inside A
#: exit A
```

`with trace("A") as t:` runs the body of `trace()` up to the `yield`,
printing `enter A`.
The yielded value is what `as` binds, so `t` is `"A"`.
The block under the `with` then runs.
When it finishes, `trace()` resumes just after the `yield` and prints `exit A`.

The `finally` makes the cleanup dependable:
an exception raised in the block appears at the `yield`,
and `finally` still runs the cleanup before the exception propagates.

Leaving the `try`/`finally` out is the common mistake:

```python
# no_finally.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def careless(name: str) -> Iterator[str]:
    print(f"enter {name}")
    yield name
    print(f"exit {name}")

try:
    with careless("A"):
        raise ValueError("boom")
except ValueError as error:
    print("caught:", error)
#: enter A
#: caught: boom
```

Without the `try`/`finally`,
Python resumes the generator by raising the block's exception at the `yield`,
so the code after the `yield` never runs and `exit A` never prints.
Nothing warns you: the generator silently skips the cleanup on the one path where it matters most.
Wrap the `yield` in `try`/`finally` in every `@contextmanager` generator.

One caution: the manager object `trace("A")` returns is single-use.
Its generator runs once,
so reusing the same object in a second `with` fails with a message that names nothing useful:
`AttributeError: '_GeneratorContextManager' object has no attribute 'args'`.
Construct a fresh manager for each `with` statement.
A loop around the `yield` cannot work around this:
`@contextmanager` enforces the single `yield`,
and a generator that reaches a second `yield` makes the manager raise a `RuntimeError`
(`generator didn't stop`) when the block ends.

## The Protocol

How does `with` know what to run?
It knows nothing about generators or `@contextmanager`.
A *context manager* is any object that implements two methods: `__enter__()`,
which runs at the start of the block, and `__exit__()`, which runs at the end.
`@contextmanager` manufactures such an object from a generator function.
Writing the class by hand shows the machinery directly.
Every hand-written context manager class in this chapter keeps `__init__()` in longhand rather than becoming a `@dataclass`,
so nothing between the class statement and the two protocol methods needs decoding:

```python
# trace_cm.py
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

if __name__ == "__main__":
    with Trace("A") as t:
        print(f"inside {t.name}")
#: enter A
#: inside A
#: exit A
```

`with Trace("A") as t:` takes these steps:

1. Evaluate `Trace("A")` to produce a manager object.
2. Call the manager's `__enter__()`.
3. Bind `__enter__()`'s return value to `t`.
4. Run the block.
5. Call the manager's `__exit__()`, no matter how the block finished.

`__enter__()` returns the object that `as` binds, often `self`.
The return annotation `Self`
(introduced in [Static Typing](08_Static_Typing.md#the-self-type))
declares an instance of the enclosing class.
`__exit__()` takes three arguments describing any exception (covered below).

Comparing this to the generator form,
`__enter__()` is the portion before the `yield`.
`__exit__()` is the portion after it.

`Trace` is also reusable: the same instance can appear in a second `with`,
because `__enter__()` just runs again.
The generator form cannot, which is the single-use caution above.
A class manager that stores per-`with` state keeps that property only if `__enter__()` resets it.

The generator form is usually the clearest choice.
Use a class when the manager needs to hold methods or state beyond a single setup and teardown.

## Guaranteed Cleanup

Here, `__exit__()` runs when the block raises an exception,
but before the exception propagates:

```python
# exit_on_error.py
from trace_cm import Trace

try:
    with Trace("A"):
        raise ValueError("boom")
except ValueError as error:
    print("caught:", error)
#: enter A
#: exit A
#: caught: boom
```

`exit A` prints before `caught`, so the cleanup runs on the exception path.
This is the same guarantee a `try`/`finally` gives,
packaged as a reusable object.

The guarantee covers the block, not the setup:

```python
# enter_fails.py

class Fragile:
    def __enter__(self) -> None:
        print("enter fails")
        raise RuntimeError("no resource")

    def __exit__(self, *exc: object) -> bool:
        print("exit runs")
        return False

try:
    with Fragile():
        print("body")
except RuntimeError as error:
    print("caught:", error)
#: enter fails
#: caught: no resource
```

`exit runs` never prints,
because Python only registers the cleanup once `__enter__()` returns.
An `__enter__()` that acquires several things must clean up its own partial work before it raises an exception.
[`ExitStack`](#combining-context-managers), later in this chapter,
is the standard tool for that:
it unwinds whatever it already entered when a later entry fails.
In a `with` naming several managers this is per-manager:
the ones that entered successfully still exit,
and only the failing one gets no `__exit__()` call.

## The `__exit__()` Arguments

`__exit__(self, exc_type, exc, tb)` receives the details of an exception raised in the block.
When the block finishes normally, all three are `None`.
When it raises an exception, they hold the exception's class, its instance,
and its traceback object.
`Trace.__exit__()` above types `exc` and `tb` as `object`,
the most general type, since it never inspects either one.

The return value decides that exception's fate.
A falsy value lets it propagate;
this includes the implicit `None` of a method with no `return`,
so the exception propagates by default.
A truthy value *suppresses* it: the `with` statement swallows the exception,
and execution continues after the block.

A generator manager suppresses by catching:

```python
# suppress_in_generator.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def ignoring(kind: type[BaseException]) -> Iterator[None]:
    try:
        yield
    except kind as error:
        print(f"swallowed {error!r}")

with ignoring(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")
print("survived")
#: before
#: swallowed ZeroDivisionError('division by zero')
#: survived
```

A generator manager has no return value to set.
The exception arrives at the `yield`,
so catching it there and not re-raising is the equivalent of `__exit__()` returning `True`.
Letting it out of the `except` clause, or omitting the clause,
is the equivalent of returning a falsy value.

The standard library provides this behavior ready-made,
as `contextlib.suppress`:

```python
# suppress_exceptions.py
from contextlib import suppress

with suppress(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs
#: before
print("survived")
#: survived
```

`suppress` is a class named like a function because you use it like one.
See [Naming Conventions](02_Tour.md#naming-conventions)
for when a class departs from `CapWords`.

Writing your own version as a class shows the suppression directly,
in the two lines that decide the return value:

```python
# ignore_one.py

class ignore_one:
    def __init__(self, kind: type[BaseException]) -> None:
        self.kind = kind

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if (exc_type is not None
            and issubclass(exc_type, self.kind)):
            print(f"{exc!r}")
            return True
        return False

with ignore_one(ZeroDivisionError):
    print("before")
    1 / 0
    # Never runs: the error jumps to __exit__
    print("after")
print("survived")
#: before
#: ZeroDivisionError('division by zero')
#: survived
```

`__exit__()` receives `exc_type: type[BaseException] | None` because Python passes it the raised exception's class,
or `None` when the block finishes cleanly.
[`type[...]`](08_Static_Typing.md#classes-as-values-type) means the class,
such as `ZeroDivisionError`, not an instance of it.
`issubclass(cls, classinfo)` returns `True` if `cls` is `classinfo` or a subclass of it,
so a `ZeroDivisionError` still matches `ignore_one(ArithmeticError)`.
`exc!r` prints the exception's `repr()`,
which includes both its type and its arguments, not just `exc_type.__name__`.
`__enter__()` returns `None` because this manager has nothing to hand to `as`.
You can still write `as`, but it binds `None`.

A fuller version of the same idea takes several types at once,
and accepts no argument to mean "ignore everything."
It is useful enough to reuse elsewhere in the book, so it lives in `utils/`,
where any chapter can import it:

```python
# utils/exceptions.py

ALL = sentinel("ALL")
type Types = (type[BaseException]
              | tuple[type[BaseException], ...])

class ignore:
    def __init__(self, types: Types | ALL = ALL) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if exc_type is None:
            return False
        if self.types is not ALL:
            if not issubclass(exc_type, self.types):
                return False
        print(f"{exc!r}")
        return True
```

`ignore` adds two things to `ignore_one`.
The first is the tuple form:
`issubclass()` accepts a tuple of classes as its second argument,
matching if `cls` is a subclass of any one of them,
so `ignore((ZeroDivisionError, TypeError))` covers several types in one manager.
The `Types` alias names that "one class or a tuple of classes" shape once instead of writing it out at every use.

The second is the default.
The constructor's `types` parameter defaults to the `ALL` [sentinel](05_Functions.md#default-and-keyword-arguments),
which makes `ignore()` with no argument catch everything.
`self.types is not ALL` [narrows](08_Static_Typing.md#narrowing)
`self.types` from `Types | ALL` down to `Types`,
since ruling out `ALL` leaves only `Types`.
By the time `issubclass(exc_type, self.types)` runs,
narrowing has confirmed `self.types` is a `Types`,
and the earlier `if exc_type is None: return False` has confirmed `exc_type` is not `None`.

`suppress` reads the same call the opposite way:
`suppress()` with no argument suppresses nothing,
because a raised exception has no listed type to match.
An `ignore()` that catches everything also catches `KeyboardInterrupt` and `SystemExit`,
so name the types you expect unless you really want a block that nothing escapes.

```python
# demo_exceptions.py
from exceptions import ignore

with ignore(ZeroDivisionError):
    print("before")
    1 / 0
    # Never runs: the error jumps to __exit__
    print("after")
print("survived")
#: before
#: ZeroDivisionError('division by zero')
#: survived

with ignore():  # No argument means ALL
    print("before")
    raise KeyError("anything")
print("survived")
#: before
#: KeyError('anything')
#: survived

with ignore() as x:
    print(f"{x = }")
#: x = None
```

The `1 / 0` raises an exception, `__exit__()` prints which exception it ignores,
then returns `True`,
and the `with` statement absorbs the error so `survived` still prints.

In the last example, `x` receives the return value of `__enter__()`,
which for `ignore()` is `None`.

## Context Manager as Decorator

A context manager brackets a block of statements: setup before, cleanup after.
A typical decorator from [Decorators](14_Decorators.md)
brackets a function call the same way.
`contextlib.ContextDecorator` connects the two:
a subclass works both as a context manager and as a decorator.
Every manager `@contextmanager` produces already inherits from `ContextDecorator`,
so `banner` works as a decorator,
even though `ContextDecorator` never appears in it:

```python
# context_decorator.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Iterator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

@banner("report")
def report() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    report()
    with banner("meeting"):
        print("agenda")
#: === report ===
#: quarterly numbers
#: === report ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
```

`banner` works as both a decorator for `report` and in a `with` in `__main__`.
The parentheses in `@banner("report")` matter: the call constructs the manager,
which then decorates the function.
Each call of the decorated function builds a fresh manager,
so you can call `report()` any number of times,
each with its own enter and exit.
The single-use caution from earlier still holds for the manager object you name in a `with`.
The machinery applies `functools.wraps`,
so `report` keeps its name and docstring
(see [Maintaining the Wrapped Interface](14_Decorators.md#maintaining-the-wrapped-interface)).

Here's the same `banner` as a class.
This time it inherits from `ContextDecorator`:

```python
# banner_cm.py
from contextlib import ContextDecorator

class banner(ContextDecorator):
    def __init__(self, title: str) -> None:
        self.title = title

    def __enter__(self) -> None:
        print(f"=== {self.title} ===")

    def __exit__(self, *exc: object) -> bool:
        print(f"=== {self.title} ends ===")
        return False

@banner("report")
def report() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    report()
    with banner("meeting"):
        print("agenda")
#: === report ===
#: quarterly numbers
#: === report ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
```

Like `suppress` and `ignore`,
the class version of `banner` uses a lowercase name because you use it like a function.
`__exit__(self, *exc: object)` collects the three arguments into a tuple the method never reads,
which is the shorter way to write a cleanup that does not care why the block ended.
Unlike the generator form,
the class form re-enters the same instance on every call to `report()`,
so every call shares any state the instance holds.

Neither version of `banner` can rewrite arguments, inspect the return value,
or skip the call.
A decorator like [`repeat`](14_Decorators.md#decorators-that-take-arguments)
or [`hijack`](14_Decorators.md) can do all three,
because it defines its own wrapper function directly,
with full access to `*args`, `**kwargs`, and the return value.
`banner`'s wrapper comes from `ContextDecorator`
(directly in `banner_cm.py`, or by way of `@contextmanager` in `context_decorator.py`),
and that wrapper always calls the function once, unchanged,
with setup before it and cleanup after.
Even if `report()` takes arguments or returns a value,
neither version of `banner` sees them.
`banner` offers one definition instead,
usable both as a `with` block and as a `@` decorator.
Use it when setup and cleanup should be identical on every call.

## Combining Context Managers

A single `with` can include several managers, separated by commas.
They enter left to right and exit in reverse:

```python
# multiple.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

with tag("ul") as outer, tag("li") as inner:
    print(f"  {outer} then {inner}")
#: <ul>
#: <li>
#:   ul then li
#: </li>
#: </ul>
```

When the managers do not fit on one line,
parentheses group them without changing the behavior:

    with (tag("ul") as outer,
          tag("li") as inner):
        ...

When you do not know the number of managers until runtime,
`contextlib.ExitStack` holds a dynamic set of managers and unwinds them in reverse when the block ends:

```python
# exit_stack.py
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
        open_tags = [
            stack.enter_context(tag(n)) for n in names]
        print("using", open_tags)

wrap(["a", "b"])
#: open a
#: open b
#: using ['a', 'b']
#: close b
#: close a
wrap(["a", "b", "c"])
#: open a
#: open b
#: open c
#: using ['a', 'b', 'c']
#: close c
#: close b
#: close a
```

`wrap()` does not know how many managers it will enter until it runs,
which is the case a comma-separated `with` cannot express.

## The `contextlib` Toolkit

The `contextlib` module provides ready-made managers.
Choose these before writing `__enter__()` and `__exit__()` by hand.

- `suppress(*exceptions)` ignores the listed exceptions,
  replacing the `ignore` class above.
- `closing(obj)` calls `obj.close()` on exit,
  for objects that have `close()` but are not context managers themselves.
- `ExitStack` manages a dynamic or conditional set of managers, as shown above.
- `ContextDecorator` lets a context manager double as a decorator,
  as shown above.
- `nullcontext(value)` is a do-nothing manager whose `__enter__()` returns `value`,
  useful when a `with` is optional and one code path should cover it.

A function might write to a path it opens itself,
to a stream the caller hands it, or to standard output by default.
The function should close only the first of those when it finishes.
`nullcontext` lets a single `with` block serve all three cases:

```python
# nullcontext_demo.py
import sys
import tempfile
from contextlib import AbstractContextManager, nullcontext
from io import StringIO
from pathlib import Path
from typing import IO

def emit(lines: list[str],
         out: IO[str] | Path | None = None) -> None:
    manager: AbstractContextManager[IO[str]]
    match out:
        case Path():
            manager = out.open("w")
        case None:
            manager = nullcontext(sys.stdout)
        case _:
            manager = nullcontext(out)
    with manager as stream:
        for line in lines:
            print(line, file=stream)

emit(["alpha", "beta"])  # Default: stdout, left open
#: alpha
#: beta
buffer = StringIO()
emit(["gamma"], buffer)  # Caller's stream, left open
print(buffer.getvalue().strip(), buffer.closed)
#: gamma False
path = Path(tempfile.gettempdir()) / "emit.txt"
# emit() opened it, so emit() closes it
emit(["delta"], path)
print(path.read_text().strip())
#: delta
path.unlink()
```

`AbstractContextManager[IO[str]]` is the type of any context manager whose `__enter__()` returns an `IO[str]`,
so one variable can hold the open file in one branch and a `nullcontext` in the others.

`emit()` closes only the file it opened.
A stream the caller handed over stays open, which the caller expects:
exiting a `nullcontext` does nothing,
so the same `with` block closes the file in the `Path` branch and touches nothing in the other two.

## The Async Protocol

`with` calls `__enter__()` and `__exit__()`.
`async with` calls `__aenter__()` and `__aexit__()`, which are coroutines,
so the setup and the cleanup can both await.
`contextlib.asynccontextmanager` builds one from an async generator,
the same way `@contextmanager` builds the synchronous form,
and `AsyncExitStack` is the `ExitStack` equivalent:

```python
# async_manager.py
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

@asynccontextmanager
async def session(name: str) -> AsyncIterator[str]:
    print(f"open {name}")
    await asyncio.sleep(0.01)  # Setup that waits
    try:
        yield name
    finally:
        await asyncio.sleep(0.01)  # Cleanup that waits
        print(f"close {name}")

async def main() -> None:
    async with session("db") as s:
        print(f"using {s}")

asyncio.run(main())
#: open db
#: using db
#: close db
```

This is the generator form with `async` in front of it.
`asyncio.run()` starts the event loop those awaits need,
which [Concurrency](19_Concurrency.md) covers.
Everything this chapter says about ordering, the three exception arguments,
and suppression through a truthy return applies unchanged.
That chapter uses `async with` throughout, for `asyncio.TaskGroup`, locks,
and semaphores; each of those is an object with the two `a`-prefixed methods.

## An Object Pool

Some objects are expensive to create or rationed by the outside world:
database connections, worker processes, licensed sessions.
The *Object Pool* pattern creates a fixed group of these expensive objects and lends them out.
Lending is the dangerous half.
Every borrower must return the object on every path out of their code,
including the exception path,
or the pool slowly drains until the program starves.
A context manager can guarantee that every borrowed object comes back.
In Python, a pool is a queue plus a `@contextmanager` method:

```python
# object_pool.py
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from queue import Queue

@dataclass(frozen=True)
class Connection:
    number: int

    def query(self, sql: str) -> str:
        return f"connection {self.number}: {sql}"

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

if __name__ == "__main__":
    pool = Pool(Connection(1), Connection(2))
    with pool.lease() as conn:
        print(conn.query("SELECT name FROM users"))
        print("available during lease:", pool.available())
    print("available after lease:", pool.available())
    with suppress(RuntimeError), pool.lease():
        raise RuntimeError("crash during query")
    print("available after crash:", pool.available())
#: connection 1: SELECT name FROM users
#: available during lease: 1
#: available after lease: 2
#: available after crash: 2
```

`lease()` takes an item out of the queue, yields it to the `with` block,
and the `finally` puts it back.
The crash inside the second `with` block still returns the connection,
so the count is back to two.
`Pool` is generic over the pooled type,
and it never creates or destroys anything.
It only tracks custody.

The queue does more than store the idle items.
`Queue` is thread-safe, and `get()` blocks while the pool is empty,
so a borrower waits until someone else's `with` block ends and a return makes an item available.
Handing the same pool to several threads makes it the throttle that limits concurrent use,
which is how real database connection pools behave.
`available()` is a snapshot for the demo, not a synchronization primitive:
`Queue.qsize()` is only approximate once more than one thread is borrowing,
because another thread can lease or return between the count and its use.

This differs from [Flyweight](35_Flyweight.md), its nearest neighbor.
A flyweight is immutable and shared by everyone at once.
A pooled object is usually mutable or stateful,
so the pool lends it to one borrower at a time,
and the lease exists to take it back.

Three tests pin down what the lease guarantees:
the item leaves the pool and comes back,
it comes back even when the block raises an exception,
and the pool hands out the same object rather than a new one:

```python
# test_object_pool.py
import pytest
from object_pool import Connection, Pool

def test_lease_removes_then_returns() -> None:
    pool = Pool(Connection(1), Connection(2))
    with pool.lease():
        assert pool.available() == 1
    assert pool.available() == 2

def test_returned_on_exception() -> None:
    pool = Pool(Connection(1))
    with pytest.raises(RuntimeError):
        with pool.lease():
            raise RuntimeError("boom")
    assert pool.available() == 1

def test_objects_reused_not_recreated() -> None:
    pool = Pool(Connection(1))
    with pool.lease() as first:
        pass
    with pool.lease() as second:
        assert second is first
```

A production pool adds refinements to this skeleton,
such as lazily creating items on first demand,
validating an item before lending it out,
and a timeout on `get()` so a starved borrower fails loudly instead of waiting forever.

Each of those refinements is a change inside `lease()`,
invisible to every `with pool.lease()` in the codebase.
That is the protocol's payoff:
the borrower's contract is two lines long and impossible to get wrong,
and everything hard about custody lives on the other side of the `yield`.

## Choosing a Form

Four forms give you a context manager.
Try them in this order.
Use a `contextlib` manager when one fits, since `suppress`, `closing`,
`nullcontext`, and `ExitStack` cover most of what people write by hand.
Otherwise write a generator with `@contextmanager`,
which is the shortest thing that can express setup, teardown,
and a `try`/`finally` between them.
Write a class with `__enter__()` and `__exit__()` when the manager needs state,
methods beyond the two protocol ones, or reuse across several `with` statements,
which the generator form cannot do.
Add `ContextDecorator` only when the same bracket should also wrap whole functions.

Whichever form you choose, the borrower's side contains two lines,
and every change you make later goes inside the manager.

## Exercises

1.  In `trace_cm.py`, nest a second `with Trace("B") as u:` block inside the body of the first `with Trace("A") as t:` block,
    with its own `print(f"inside {u.name}")`.
    Predict the order the six "enter"/"inside"/"exit" lines appear in before running it.
2.  In `demo_exceptions.py`,
    change `ignore(ZeroDivisionError)` to `ignore((ZeroDivisionError, TypeError))`,
    then raise a `TypeError` instead of dividing by zero,
    and confirm that `ignore` suppresses it too.
3.  Add a third manager to the `with` statement in `multiple.py`,
    `tag("li")` again for a second item,
    and confirm the exit order still reverses the entry order.
4.  In `test_object_pool.py`, add a test that leases both connections at once,
    entering a second `with pool.lease()` block inside the first,
    and confirms `pool.available()` reaches `0`.
5.  Stack `@banner("outer")` and `@banner("inner")` from `context_decorator.py` on a single function and predict the order of the four bracketing lines before running it.
6.  Write a context manager `ignore_missing` whose `__exit__()` suppresses only `KeyError` and lets everything else through,
    without using `contextlib.suppress`.
    Test it with a block that raises a `KeyError` and a block that raises a `ValueError`.
7.  Rewrite `exit_stack.py` to take its names from `sys.argv[1:]`,
    run it with no arguments and with three,
    and confirm the close order reverses the open order in both cases.
