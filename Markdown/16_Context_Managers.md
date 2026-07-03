# Context Managers

The `with` statement, introduced in [Control Flow](04_Control_Flow.md#context-managers),
runs setup before a block and cleanup after it, even if the block raises an exception.
This chapter shows what `with` actually does and how to write your own context managers.

A *context manager* is any object that implements two methods: `__enter__()`,
which runs at the start of the block, and `__exit__()`, which runs at the end.
The `with` statement calls them for you and guarantees that `__exit__()` runs
no matter how the block finishes.

Thus, the context manager introduces a scope that determines when initialization and cleanup happen.
This is far more reliable than using `__del__()`, as we saw in [Cleanup](10_Cleanup.md).

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
The return annotation `Self`
(introduced in [Static Typing](08_Static_Typing.md#the-self-type))
declares exactly that: an instance of the enclosing class.
`__exit__()` takes three arguments describing any exception (covered below).
A `with` block guarantees that the exit code runs at the end of the scope.

## Cleanup Is Guaranteed

Context managers make code shorter, but the point is the guarantee.
Here, `__exit__()` runs when the block raises an exception, but before the exception propagates:

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
This is the same guarantee a `try`/`finally` gives, packaged as a reusable object.

## The `__exit__()` Arguments

`__exit__(self, exc_type, exc_value, traceback)` receives the details of an
exception raised in the block.
When the block finishes normally, all three are `None`.
When it raises an exception, they hold the exception's type, value, and traceback.

The return value decides what happens to that exception.
A `False` value (including `None`) lets it propagate.
A `True` value *suppresses* it.
The `with` statement swallows the exception and
execution continues after the block:

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

The `1 / 0` raises an exception, `__exit__()` returns `True`, and the `with` statement
absorbs the error so `survived` still prints.

The annotations use [`type[...]`](08_Static_Typing.md#classes-as-values-type),
which means the exception *class* itself, such as `ZeroDivisionError`, not an instance of it.
`__init__()` takes `*types: type[BaseException]`, so `Ignore(ZeroDivisionError)`
collects the exception classes you hand it into the `types` tuple.
`__exit__()` receives `exc_type: type[BaseException] | None` because Python passes it
the class of the exception that was raised, or `None` when the block finished cleanly.
That class is what `issubclass(exc_type, self.types)` checks against the classes you
chose to suppress.

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

`suppress` is a class, but it is named like a function because you use it like one.
See [Naming Conventions](02_Tour.md#naming-conventions) for when a class departs from `CapWords`.

## Context Managers as Generators

Most context managers are simpler to write as a generator.
`contextlib.contextmanager` turns a function with a single `yield` into a
context manager: the code before `yield` is the setup, the yielded value is
what `as` binds, and the code after `yield` is the cleanup.
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

This is the same setup-then-teardown shape as a `pytest` fixture that
[`yield`s its value](11_Testing.md#fixtures-replace-setup-and-teardown).
It relies on the generator and decorator machinery from [Decorators](15_Decorators.md)
and [Iterators](27_Iterators.md#generators).
The generator form is usually the clearest choice; use a class when the
manager needs to hold methods or state beyond a single setup and teardown.

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

When the number of managers is not known until runtime, `contextlib.ExitStack`
holds a dynamic set of managers and unwinds them in reverse on the way out:

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

- `suppress(*exceptions)` ignores the listed exceptions, replacing the `Ignore`
  class above.
- `closing(obj)` calls `obj.close()` on exit, for objects that have `close()`
  but are not context managers themselves.
- `ExitStack` manages a dynamic or conditional set of managers, as shown above.
- `nullcontext(value)` is a do-nothing manager that yields `value`, useful when
  a `with` is optional and you want one code path.

`nullcontext` earns its keep when only some runs have a resource to manage.
A function might take an optional file to write to, defaulting to standard output.
The default must stay open, so wrapping `sys.stdout` in `nullcontext` lets a single
`with` block serve both cases:

```python
# nullcontext_demo.py
import sys
from contextlib import nullcontext
from io import StringIO

def emit(lines: list[str], out: StringIO | None = None) -> None:
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

A real file should close on the way out; `stdout` should not.
`nullcontext(sys.stdout)` yields `stdout` but does nothing on exit,
so one `with` block serves both cases.
With a real resource the `with` closes it, shown by `buffer.closed`.
With the default, `nullcontext` hands back `sys.stdout` and does nothing on exit,
so the stream stays open.
