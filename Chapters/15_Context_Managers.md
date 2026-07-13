# Context Managers

The `with` statement,
introduced in [Control Flow](04_Control_Flow.md#context-managers),
runs setup before a block and cleanup after it,
even if the block raises an exception.
This chapter shows what `with` actually does and how to write your own context managers.

A *context manager* is any object that implements two methods: `__enter__()`,
which runs at the start of the block, and `__exit__()`, which runs at the end.
The `with` statement calls them for you and guarantees that `__exit__()` runs no matter how the block finishes.

Thus, the context manager introduces a scope that determines when initialization and cleanup happen.
This is far more reliable than using `__del__()`,
as we saw in [Cleanup](10_Cleanup.md).

## The Protocol

`with cm as name:` calls `cm.__enter__()`, binds its return value to `name`,
runs the block, then calls `cm.__exit__()`:

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

`__enter__()` returns the object that `as` binds, often `self`.
The return annotation `Self` (introduced in [Static Typing](08_Static_Typing.md#the-self-type)) declares an instance of the enclosing class.
`__exit__()` takes three arguments describing any exception (covered below).
A `with` block guarantees that the exit code runs at the end of the scope.

## Cleanup Is Guaranteed

Context managers make code shorter, but the point is the guarantee.
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

`exit A` prints before `caught`, so the cleanup happens on the way out.
This is the same guarantee a `try`/`finally` gives,
packaged as a reusable object.

## The `__exit__()` Arguments

`__exit__(self, exc_type, exc_value, traceback)` receives the details of an exception raised in the block.
When the block finishes normally, all three are `None`.
When it raises an exception, they hold the exception's type, value,
and traceback.

The return value decides what happens to that exception.
A `False` value (including `None`) lets it propagate.
A `True` value *suppresses* it.
The `with` statement swallows the exception and execution continues after the block:

```python
# suppress_cm.py
class Ignore:
    def __init__(self, *types: type[BaseException]) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: object) -> bool:
        return (exc_type is not None
                and issubclass(exc_type, self.types))

with Ignore(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs: the error jumps straight to __exit__
print("survived")
#: before
#: survived
```

The `1 / 0` raises an exception, `__exit__()` returns `True`,
and the `with` statement absorbs the error so `survived` still prints.

The annotations use [`type[...]`](08_Static_Typing.md#classes-as-values-type),
which means the exception *class* itself, such as `ZeroDivisionError`,
not an instance of it.
`__init__()` takes `*types: type[BaseException]`,
so `Ignore(ZeroDivisionError)` collects the exception classes you hand it into the `types` tuple.
`__exit__()` receives `exc_type: type[BaseException] | None` because Python passes it the raised exception's class,
or `None` when the block finished cleanly.
That class is what `issubclass(exc_type, self.types)` checks against the classes you chose to suppress.

The standard library includes its own version of `Ignore` as `contextlib.suppress`.
The above demonstration would instead be:

```python
# suppress_exceptions.py
from contextlib import suppress

with suppress(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs
print("survived")
#: before
#: survived
```

`suppress` is a class,
but it is named like a function because you use it like one.
See [Naming Conventions](02_Tour.md#naming-conventions) for when a class departs from `CapWords`.

## Context Managers as Generators

Most context managers are simpler to write as a generator.
`contextlib.contextmanager` turns a function with a single `yield` into a context manager.
The code before `yield` is the setup, the yielded value is what `as` binds,
and the code after `yield` is the cleanup.
Put the cleanup in a `finally` so it runs even if the block raises an exception:

```python
# generator_cm.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Iterator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

with tag("p") as t:
    print(f"  text in {t}")
#: <p>
#:   text in p
#: </p>
```

This is the same setup-then-teardown shape as a `pytest` fixture that [`yield`s its value](11_Testing.md#fixtures-replace-setup-and-teardown).
It relies on the generator and decorator machinery from [Decorators](14_Decorators.md) and [Iterators](23_Iterators.md#generators).
The generator form is usually the clearest choice.
Use a class when the manager needs to hold methods or state beyond a single setup and teardown.

## A Context Manager as a Decorator

A context manager brackets a block of statements: setup before, cleanup after.
A typical decorator from [Decorators](14_Decorators.md) brackets a function call the same way.
`contextlib.ContextDecorator` connects the two:
a context manager that inherits from it can be applied with `@`,
and every manager `@contextmanager` produces already inherits from it:

```python
# context_decorator.py
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def tracing(label: str) -> Iterator[None]:
    print(f"-> {label}")
    try:
        yield
    finally:
        print(f"<- {label}")

@tracing("add")
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    with tracing("block"):
        print("inside")
    print(add(2, 3))
    print(add(10, 20))
#: -> block
#: inside
#: <- block
#: -> add
#: <- add
#: 5
#: -> add
#: <- add
#: 30
```

`tracing` works both ways.
`with tracing("block"):` brackets a group of statements.
`@tracing("add")` decorates a function,
so every call to `add()` enters the context, runs `add()`, and exits.
Note the parentheses in `@tracing("add")`:
the manager is constructed first, and the manager decorates.
A generator-based manager recreates its generator on each use,
so the decorated function can be called any number of times,
each with a fresh enter and exit.
The machinery even applies `functools.wraps` for you,
so `add` keeps its name and docstring
(see [Maintaining the Wrapped Interface](14_Decorators.md#maintaining-the-wrapped-interface)).

A hand-written class opts in by inheriting from `ContextDecorator`:

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

Like `suppress`, `banner` is a class named like a function because you use it like one.
Unlike the generator form,
the class form re-enters the same instance on every call to `report()`,
so any state the instance holds is shared across calls.

The decorator form only brackets.
The manager never sees the function's arguments or return value,
cannot call the function twice like `repeat`,
and cannot decide to skip the call like `hijack`.
What it offers is one definition, usable both ways:
around a block with `with`, and on a function with `@`,
when every call deserves the same bracketing.

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

When you do not know the number of managers until runtime,
`contextlib.ExitStack` holds a dynamic set of managers and unwinds them in reverse on the way out:

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

with ExitStack() as stack:
    names = [stack.enter_context(tag(n)) for n in ("a", "b", "c")]
    print("using", names)
#: open a
#: open b
#: open c
#: using ['a', 'b', 'c']
#: close c
#: close b
#: close a
```

## The `contextlib` Toolkit

The `contextlib` module provides ready-made managers.
Choose these before writing `__enter__()` and `__exit__()` by hand.

- `suppress(*exceptions)` ignores the listed exceptions,
  replacing the `Ignore` class above.
- `closing(obj)` calls `obj.close()` on exit,
  for objects that have `close()` but are not context managers themselves.
- `ExitStack` manages a dynamic or conditional set of managers, as shown above.
- `ContextDecorator` lets a context manager double as a decorator,
  as shown above.
- `nullcontext(value)` is a do-nothing manager that yields `value`,
  useful when a `with` is optional and you want one code path.

`nullcontext` is useful when only some runs have a resource to manage.
A function might take an optional file to write to,
defaulting to standard output.
The default must stay open,
so wrapping `sys.stdout` in `nullcontext` lets a single `with` block serve both cases:

```python
# nullcontext_demo.py
import sys
from contextlib import nullcontext
from io import StringIO
from typing import IO

def emit(lines: list[str], out: IO[str] | None = None) -> None:
    manager = out if out is not None else nullcontext(sys.stdout)
    with manager as stream:
        for line in lines:
            print(line, file=stream)

emit(["alpha", "beta"])   # Defaults to stdout, left open
#: alpha
#: beta
buffer = StringIO()
emit(["gamma"], buffer)   # A managed resource, closed on exit
try:
    print(buffer.read())
except ValueError as e:
    print("ValueError:", e)
#: ValueError: I/O operation on closed file
print(buffer.closed)
#: True
```

A real file should close on the way out.
`stdout` should not.
With a real resource the `with` closes it, shown by `buffer.closed`.
With the default, `nullcontext` hands back `sys.stdout` and does nothing on exit,
so the stream stays open.

## An Object Pool

Some objects are expensive to create or rationed by the outside world:
database connections, worker processes, licensed sessions.
The *Object Pool* pattern creates a fixed set up front and lends them out.
Lending is the dangerous half.
Every borrower must return the object on every path out of their code,
including the exception path,
or the pool slowly drains until the program starves.
The context manager guarantees the "must happen on every path out,"
so in Python a pool is a queue plus one `@contextmanager` method:

```python
# object_pool.py
from collections.abc import Iterator
from contextlib import contextmanager
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
    try:
        with pool.lease() as conn:
            raise RuntimeError("crash during query")
    except RuntimeError:
        pass
    print("available after crash:", pool.available())
#: connection 1: SELECT name FROM users
#: available during lease: 1
#: available after lease: 2
#: available after crash: 2
```

`lease()` takes an item out of the queue, yields it to the `with` block,
and the `finally` puts it back.
The `finally` is the entire pattern.
The crash inside the second `with` block still returns the connection,
so the count is back to two.
`Pool` is generic over the pooled type,
and it never creates or destroys anything.
It only tracks custody.

The queue does more than store the idle items.
`Queue` is thread-safe, and `get()` blocks while the pool is empty,
so a borrower waits until someone else's `with` block ends and a return makes an item available.
Handing the same pool to several threads therefore just works.
The pool becomes the throttle that limits concurrent use,
which is how real database connection pools behave.

This differs from [Flyweight](35_Flyweight.md), its nearest neighbor.
A flyweight is immutable and shared by everyone at once.
A pooled object is usually mutable or stateful,
so the pool lends it to one borrower at a time,
and the lease exists to take it back:

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

The last test states the pattern's purpose.
The second lease hands back the same object, not a new one.
A production pool adds refinements on this skeleton,
such as creating items lazily on first demand,
validating an item before lending it out,
and a timeout on `get()` so a starved borrower fails loudly instead of waiting forever.

## Exercises

1.  In `trace_cm.py`, nest a second `with Trace("B") as u:` block inside the body of the first `with Trace("A") as t:` block,
    with its own `print(f"inside {u.name}")`.
    Predict the order the four "enter"/"inside"/"exit" lines appear in before running it.
2.  In `suppress_cm.py`, add `TypeError` to the tuple passed to `Ignore`,
    then raise a `TypeError` instead of dividing by zero,
    and confirm it is also suppressed.
3.  Add a fourth manager to the `with` statement in `multiple.py`,
    `tag("li")` again for a second item,
    and confirm the exit order still reverses the entry order.
4.  In `object_pool.py`,
    add a test (alongside the ones in `test_object_pool.py`) that leases both connections at once,
    using two separate `with pool.lease()` blocks entered one after the other without exiting the first,
    and confirms `pool.available()` reaches `0`.
5.  Stack `@tracing("outer")` and `@tracing("inner")` from `context_decorator.py` on a single function
    and predict the order of the four bracketing lines before running it.
