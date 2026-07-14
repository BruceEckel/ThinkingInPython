# Context Managers

The `with` statement,
introduced in [Control Flow](04_Control_Flow.md#context-managers),
runs setup before a block and cleanup after it,
even if the block raises an exception.
This chapter shows how to write your own context managers,
and what `with` actually does.

A context manager marks out a span of execution that determines when initialization and cleanup happen.
This is far more reliable than using `__del__()`,
as we saw in [Cleanup](10_Cleanup.md).

## A Basic Context Manager

The simplest way to write a context manager is a generator function with a single `yield`,
turned into a context manager by the `contextlib.contextmanager` decorator:

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
which prints `enter A`.
The yielded value is what `as` binds, so `t` is `"A"`.
The block under the `with` then runs.
When it finishes, `trace()` resumes just after the `yield` and prints `exit A`.

The code before `yield` is the setup, and the code after it is the cleanup.
The `finally` is what makes the cleanup dependable:
an exception raised in the block appears at the `yield`,
and `finally` runs the cleanup anyway, before the exception propagates.
This is the same setup-then-teardown shape as a `pytest` fixture that [`yield`s its value](11_Testing.md#fixtures-replace-setup-and-teardown).
It relies on the generator and decorator machinery from [Decorators](14_Decorators.md)
and [Iterators](23_Iterators.md#generators).

One caution: the manager object `trace("A")` returns is single-use.
Its generator runs once,
so reusing the same object in a second `with` raises an exception.
Construct a fresh manager for each `with` statement.

## The Protocol

How does `with` know what to run?
It knows nothing about generators or `@contextmanager`.
A *context manager* is any object that implements two methods: `__enter__()`,
which runs at the start of the block, and `__exit__()`, which runs at the end.
`@contextmanager` manufactures such an object from a generator function.
Writing the class by hand shows the machinery directly:

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

The generator form is usually the clearest choice.
Use a class when the manager needs to hold methods or state beyond a single setup and teardown.

## Cleanup Is Guaranteed

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
A falsy value lets it propagate;
this includes the implicit `None` of a method with no `return`,
so propagation is the default.
A truthy value *suppresses* it: the `with` statement swallows the exception,
and execution continues after the block.

The standard library provides this behavior ready-made,
as `contextlib.suppress`:

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

`suppress` is a class named like a function because you use it like one.
See [Naming Conventions](02_Tour.md#naming-conventions)
for when a class departs from `CapWords`.

We can write a version with more features:
reporting which exception it swallowed,
and accepting no argument to mean "ignore everything":

```python
# exceptions.py

ALL = sentinel("ALL")
type Types = type[BaseException] | tuple[type[BaseException], ...]

class ignore:
    def __init__(self, types: Types | ALL = ALL) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: object) -> bool:
        if exc_type is None:
            return False
        if self.types is not ALL:
            if not issubclass(exc_type, self.types):
                return False
        print(f"ignoring {exc!r}")
        return True
```

The constructor's `types` parameter defaults to the `ALL` [sentinel](05_Functions.md#default-and-keyword-arguments).
This makes `ignore()` with no argument catch all exceptions.
`ignore(ZeroDivisionError)` narrows that to one type.
`ignore((ZeroDivisionError, TypeError))` narrows it to several.

`__enter__()` returns `None` because `ignore` is not meant to be used with `as`.
You can still use `as` but it will just bind to `None`.

`__exit__()` receives `exc_type: type[BaseException] | None` because Python passes it the raised exception's class,
or `None` when the block finished cleanly.

`self.types is not ALL` [narrows](08_Static_Typing.md#narrowing)
`self.types` back down to `Types` (if it's not `ALL` it must be `Types`).
`issubclass(cls, classinfo)` returns `True` if `cls` is `classinfo` or a subclass of it.
It also accepts a tuple of classes for `classinfo`,
matching if `cls` is a subclass of any one of them.
Because of narrowing, by the time `issubclass(exc_type, self.types)` is called, `exc_type` is known to be a `Types`.

`exc!r` prints the exception's `repr()`,
which includes both its type and its arguments, not just `exc_type.__name__`.

The annotations use `type[BaseException]`,
a [`type[...]`](08_Static_Typing.md#classes-as-values-type) annotation,
which means the exception *class* itself, such as `ZeroDivisionError`,
not an instance of it.
That class, `exc_type` is what `issubclass(exc_type, self.types)` checks against the `self.types`, the supressed classes.

```python
# demo_exceptions.py
from exceptions import ignore

with ignore(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")  # Never runs: the error jumps straight to __exit__
print("survived")
#: before
#: ignoring ZeroDivisionError('division by zero')
#: survived

with ignore():  # No argument means ALL
    print("before")
    raise KeyError("anything")
print("survived")
#: before
#: ignoring KeyError('anything')
#: survived

with ignore() as x:
    print(f"{x = }")
#: x = None
```

The `1 / 0` raises an exception,
`__exit__()` prints which exception it is ignoring, then returns `True`,
and the `with` statement absorbs the error so `survived` still prints.

In the last example, `x` receives the return value of `__enter__()`,
which for `ignore()` is `None`.

## A Context Manager as a Decorator

A context manager brackets a block of statements: setup before, cleanup after.
A typical decorator from [Decorators](14_Decorators.md)
brackets a function call the same way.
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
so every call to `add()` enters the context, runs the original `add()`,
and exits.
Note the parentheses in `@tracing("add")`: the call constructs the manager,
which then decorates the function.
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
What it offers is one definition, usable both ways: around a block with `with`,
and on a function with `@`, when every call deserves the same bracketing.

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
  replacing the `ignore` class above.
- `closing(obj)` calls `obj.close()` on exit,
  for objects that have `close()` but are not context managers themselves.
- `ExitStack` manages a dynamic or conditional set of managers, as shown above.
- `ContextDecorator` lets a context manager double as a decorator,
  as shown above.
- `nullcontext(value)` is a do-nothing manager that yields `value`,
  useful when a `with` is optional and you want one code path.

Only some runs may have a resource to manage.
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
    Predict the order the six "enter"/"inside"/"exit" lines appear in before running it.
2.  In `demo_exceptions.py`,
    change `ignore(ZeroDivisionError)` to `ignore((ZeroDivisionError, TypeError))`,
    then raise a `TypeError` instead of dividing by zero,
    and confirm it is also suppressed.
3.  Add a third manager to the `with` statement in `multiple.py`,
    `tag("li")` again for a second item,
    and confirm the exit order still reverses the entry order.
4.  In `object_pool.py`, add a test
    (alongside the ones in `test_object_pool.py`)
    that leases both connections at once,
    using two separate `with pool.lease()` blocks entered one after the other without exiting the first,
    and confirms `pool.available()` reaches `0`.
5.  Stack `@tracing("outer")` and `@tracing("inner")` from `context_decorator.py` on a single function and predict the order of the four bracketing lines before running it.
