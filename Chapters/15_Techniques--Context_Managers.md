# Context Managers

> Whatever you acquire must be released, on every path out,
> including the one an exception takes.
> A context manager pairs acquisition with release so cleanup always runs.

The [`with` statement](04_Foundations--Control_Flow.md#context-managers)
marks out a span of execution.
It runs setup before a block and cleanup after it,
whether the block finishes normally or raises an exception.
That guarantee is far more reliable than the [`__del__()` approach](10_Foundations--Cleanup.md).
Writing your own context managers shows how `with` works.

By the end of the chapter, borrowing a pooled connection takes two lines:

```python
with pool.lease() as conn:
    conn.query("SELECT name FROM users")
```

`lease()` puts the connection back in the [pool](#an-object-pool)
on every path out of that block, including the exception path.
That `with` block is all the borrower writes.

## A Basic Context Manager

The simplest way to write a context manager is a [generator](22_Patterns--Iterators.md#generators)
function with a single `yield`.
The `contextlib.contextmanager` decorator turns that function into a context manager.
[Generators](45_Effects--Generators.md) covers the two-way form of `yield`.
The `yield` here works the way it does in a `pytest` fixture that [`yield`s its value](11_Techniques--Testing.md#fixtures-replace-setup-and-teardown).
Everything before the `yield` is setup.
Everything after it is cleanup.
That shape is all a context manager needs.

```python
# trace_gen.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def trace(name: str) -> Generator[str]:
    print(f"enter {name}")  # Setup
    try:
        yield name  # The block runs here
    finally:
        print(f"exit {name}")  # Cleanup

if __name__ == "__main__":
    with trace("A") as t:
        print(f"inside {t}")
    manager = trace("B")
    with manager:
        pass
    try:
        with manager:  # [1]
            pass
    except AttributeError as error:
        print(error)
#: enter A
#: inside A
#: exit A
#: enter B
#: exit B
#: '_GeneratorContextManager' object has no attribute 'args'
```

`as` binds the yielded value, so `t` is `"A"`.
When the block finishes,
`trace()` resumes just after the `yield` and prints `exit A`.

`trace()` produces values alone,
the shape that [Iterators](22_Patterns--Iterators.md#generators)
annotates `Iterator[T]`.
Every `@contextmanager` generator in this book carries `Generator` instead,
because the decorator calls the generator's `throw()` method,
a method of `Generator` and not of `Iterator`,
and `ty` reports the `Iterator[str]` form as deprecated.

The manager object `trace()` returns is single-use.
Its generator runs once,
so the `with manager:` at `[1]` raises an `AttributeError`.
The error message blames a missing `args` attribute for what is really a spent manager.
A loop around the `yield` leaves the manager single-use too,
because `@contextmanager` allows one `yield`.
If the generator reaches a second `yield` after the block ends,
the manager raises `RuntimeError: generator didn't stop`.
Construct a fresh manager for each `with` statement.

The `finally` makes the cleanup dependable.
`@contextmanager` raises the block's exception at the `yield`,
and `finally` runs the cleanup before the exception propagates.

Leaving the `try`/`finally` out is the common mistake:

```python
# no_finally.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def careless(name: str) -> Generator[str]:
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

`@contextmanager`'s `__exit__()` calls the generator's `throw()` method,
which resumes the generator by raising the block's exception at the `yield`.
Without the `try`/`finally`, that exception leaves the generator at once,
so the code after the `yield`, `exit A` included, never runs.
On the exception path the generator skips the cleanup in silence.
Wrap the `yield` in `try`/`finally` in every `@contextmanager` generator.

## The Protocol

What does `with` call?
It calls the same two methods on every manager,
whether `@contextmanager` built it from a generator or a class defined it.
A *context manager* is any object that implements two methods: `__enter__()`,
which runs at the start of the block, and `__exit__()`, which runs at the end.
`@contextmanager` builds such an object from a generator function.

Every hand-written context manager class in this chapter writes `__init__()` out rather than using `@dataclass`,
so the constructor sits in the listing beside the two protocol methods:

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
    manager = Trace("B")
    with manager:
        pass
    with manager:
        pass
#: enter A
#: inside A
#: exit A
#: enter B
#: exit B
#: enter B
#: exit B
```

Python runs `with Trace("A") as t:` in five steps:

1. Evaluate `Trace("A")` to produce a manager object.
2. Call the manager's `__enter__()`.
3. Bind `__enter__()`'s return value to `t`.
4. Run the block.
5. Call the manager's `__exit__()`, however the block finished.

`__enter__()` returns the object that `as` binds, often `self`.
The return annotation [`Self`](08_Foundations--Static_Types.md#the-self-type)
declares an instance of the class on which you call the method,
so on a subclass the return type is the subclass.

The three parameters of `__exit__()` describe the exception that ended the block.
Every block in `trace_cm.py` ends normally, so all three are `None`.

In generator terms, `__enter__()` is the portion before the `yield`.
`__exit__()` is the portion after it.

`Trace` is also reusable.
The demo enters the same `manager` in two `with` statements,
and both print `enter B` and `exit B`,
because `Trace.__enter__()` prints `self.name`, which a `with` leaves in place.
In `trace_gen.py` the second of those statements raises an `AttributeError`,
because a generator manager is single-use.
A class manager that stores per-`with` state stays reusable only if `__enter__()` resets that state.

The generator form is usually the shorter one, with setup, `yield`,
and cleanup in one function.
Use a class when the manager needs to hold methods or state beyond a single setup and teardown.

## Guaranteed Cleanup

When the block raises an exception,
`__exit__()` runs before the exception propagates:

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
That ordering is the same guarantee a `try`/`finally` gives.
`Trace` packages it as a reusable object.

The guarantee covers the block, not the setup:

```python
# enter_fails.py

class Fragile:
    def __enter__(self) -> None:
        print("enter fails")
        raise RuntimeError("no resource")

    def __exit__(self, *exc: object) -> None:
        print("exit runs")

try:
    with Fragile():
        print("body")
except RuntimeError as error:
    print("caught:", error)
#: enter fails
#: caught: no resource
```

`exit runs` is missing from the output,
because Python registers the cleanup when `__enter__()` returns,
and this `__enter__()` raises an exception.
A `with` that lists several managers applies the same rule per manager.
The ones that entered still exit.
The failing one gets no `__exit__()` call.
The statement stops at the failing manager,
before Python evaluates the managers listed after it.

An `__enter__()` that acquires several things must clean up its own partial work before it raises an exception.
[`ExitStack`](#combining-context-managers), later in this chapter,
is the standard tool for that.
When a later entry fails, `ExitStack` unwinds the managers it entered earlier.

`Fragile.__exit__(self, *exc: object)` collects the three arguments into a tuple the method ignores.
That shorter form suits a cleanup that ignores how the block ended.

The guarantee also assumes that cleanup succeeds.
Cleanup can fail.
When `__exit__()` raises an exception,
that new exception replaces the block's original one.
Python keeps the original only as the new exception's `__context__`:

```python
# exit_masks.py

class BrokenCleanup:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> None:
        raise ValueError("cleanup error")

try:
    with BrokenCleanup():
        raise KeyError("original")
except ValueError as error:
    print("caught:", repr(error))
    print("context:", repr(error.__context__))
#: caught: ValueError('cleanup error')
#: context: KeyError('original')
```

`KeyError('original')` never propagates to the `except`.
Python keeps the `KeyError` as `error.__context__`,
the same chaining it applies when an `except` block raises an exception.

One of the most common context-manager bugs is a cleanup that raises an exception in place of the real failure.
Write `__exit__()` methods that fail only for reasons worse than the original exception.

## The `__exit__()` Arguments

`__exit__(self, exc_type, exc, tb)` receives the details of an exception raised in the block.
When the block finishes normally, all three are `None`.
When it raises an exception, they hold the exception's class, its instance,
and its traceback object.

`Trace.__exit__()` in `trace_cm.py` types `exc` and `tb` as `object`,
the most general type, since it ignores both.
A manager that reads `exc` types it as `BaseException | None`,
as `expected_one.py` does.
A manager that reads `tb` types it as `TracebackType | None`,
importing `TracebackType` from `types`.

The return value of `__exit__()` determines whether the block's exception propagates.
A falsy value lets it propagate.
Falsy includes the implicit `None` of a method with no `return`,
so the exception propagates by default.
A truthy value suppresses it.
The `with` statement swallows the exception,
and execution continues after the block.

Any truthy value suppresses, not `True` alone.
An `__exit__()` that returns the result of its last cleanup call suppresses the block's exception whenever that result is truthy,
as a nonzero count or a nonempty status string is.
Annotate `__exit__()` as `-> None`, the way `Trace` does,
unless suppressing is the manager's job.
The type checker then rejects any value the method returns.

A generator manager suppresses by catching:

```python
# suppress_in_generator.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def ignoring(kind: type[BaseException]) -> Generator[None]:
    try:
        yield
    except kind as error:
        print(f"swallowed {error!r}")

with ignoring(ZeroDivisionError):
    print("before")
    1 / 0
    print("after")
#: before
#: swallowed ZeroDivisionError('division by zero')
print("survived")
#: survived
```

In a generator manager,
the `except` clause takes the place of `__exit__()`'s return value.
`@contextmanager` raises the exception at the `yield`,
so catching it there and suppressing it is the equivalent of `__exit__()` returning `True`.
Re-raising it, or omitting the `except` clause,
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

`suppress` is a class [named like a function](02_Foundations--Tour.md#naming-conventions)
because you use it like one.

A class manager suppresses through the return value of `__exit__()`:

```python
# expected_one.py

class expected_one:
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

with expected_one(ZeroDivisionError):
    print("before")
    1 / 0
    # Never runs: the error jumps to __exit__
    print("after")
#: before
#: ZeroDivisionError('division by zero')
print("survived")
#: survived
```

`__exit__()` receives `exc_type: type[BaseException] | None` because Python passes it the raised exception's class,
or `None` when the block finishes cleanly.
[`type[...]`](08_Foundations--Static_Types.md#classes-as-values-type)
means the class, such as `ZeroDivisionError`, not an instance of it.
`issubclass(cls, classinfo)` returns `True` if `cls` is `classinfo` or a subclass of it,
so a `ZeroDivisionError` still matches `expected_one(ArithmeticError)`.
`exc!r` prints the exception's `repr()`,
which includes both its type and its arguments,
where `exc_type.__name__` gives the type alone.

`__enter__()` returns `None` because `expected_one` watches the block for an exception instead of handing it an object.
An `as` clause works and binds `None`.

### The `expected` Manager

`expected` is a fuller version of `expected_one`.
It takes several types at once, and with no argument it catches everything.
Its name says how the book uses it.
The block under it should raise an exception,
and the manager prints the exception the block raised.
`expected` is useful enough to reuse elsewhere in the book,
so its definition goes in `utils/`, where any chapter can import it:

```python
# utils/exceptions.py
import textwrap
from collections.abc import Awaitable, Callable
from typing import Final

WIDTH: Final[int] = 57
ALL = sentinel("ALL")
type Types = (type[BaseException]
              | tuple[type[BaseException], ...])

def report(e: BaseException) -> None:
    line = f"[{type(e).__name__}] {e}"
    print(textwrap.fill(line, WIDTH))

class expected:
    def __init__(self, types: Types | ALL = ALL) -> None:
        self.types = types

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None,
                 tb: object) -> bool:
        if exc_type is None or exc is None:
            return False
        if self.types is not ALL:
            if not issubclass(exc_type, self.types):
                return False
        report(exc)
        return True

def expect[**P](
    types: Types, fn: Callable[P, object],
    /, *args: P.args, **kwargs: P.kwargs
) -> None:
    try:
        fn(*args, **kwargs)
    except types as e:
        report(e)
        return
    raise AssertionError("no exception raised")

async def aexpect[**P](
    types: Types, fn: Callable[P, Awaitable[object]],
    /, *args: P.args, **kwargs: P.kwargs
) -> None:
    try:
        await fn(*args, **kwargs)
    except types as e:
        report(e)
        return
    raise AssertionError("no exception raised")
```

`expected` adds two things to `expected_one`.
The first is the tuple form.
`issubclass()` accepts a tuple of classes as its second argument,
matching if `cls` is a subclass of any one of them,
so `expected((ZeroDivisionError, TypeError))` covers several types in one manager.
The `Types` alias names that "one class or a tuple of classes" shape once instead of writing it out at every use.

The second is the default.
The constructor's `types` parameter defaults to the `ALL` [sentinel](05_Foundations--Functions.md#sentinel-values),
which makes `expected()` with no argument catch everything.
`if exc_type is None or exc is None: return False` [narrows](08_Foundations--Static_Types.md#narrowing)
`exc_type` to a class and `exc` to an exception.
`self.types is not ALL` then narrows `self.types` from `Types | ALL` down to `Types`,
so `issubclass(exc_type, self.types)` type-checks.

`__exit__()` also passes the exception to `report()`,
which prints it as `[Type] message` through `textwrap.fill()` at `WIDTH`,
so a long message wraps to fit the listing width.
`expect()`, in the same file, prints through `report()` too,
so every exception the book demonstrates through `expected` or `expect()` has one form.

`suppress` treats the no-argument call the opposite way.
`suppress()` lets every exception propagate,
because its tuple of types to match is empty.
An `expected()` that catches everything also catches `KeyboardInterrupt` and `SystemExit`,
so name the types you expect unless you want the block to suppress every exception.

```python
# demo_exceptions.py
from exceptions import expected

with expected(ZeroDivisionError):
    print("before")
    1 / 0
    # Never runs: the error jumps to __exit__
    print("after")
#: before
#: [ZeroDivisionError] division by zero
print("survived")
#: survived

with expected():  # No argument means ALL
    print("before")
    raise KeyError("anything")
#: before
#: [KeyError] 'anything'
print("survived")
#: survived

with expected() as x:  # [1]
    print(f"{x = }")
#: x = None
```

In the `with` at `[1]`, `as` binds `x` to the return value of `__enter__()`,
which for `expected()` is `None`.

### The `expect()` Function

Many listings in this book call something to show the exception it raises.
`expect()` is the function form of that demonstration.
It takes the types it expects, calls `fn` with the remaining arguments,
and prints the exception as `[Type] message`,
wrapped by `textwrap.fill()` when that line is wider than `WIDTH`.
`WIDTH` is 57 because this book's listings are 60 columns wide and a `#:` output line uses three of them for its prefix.
An exception of another type propagates.
A call that returns normally fails with an `AssertionError`,
so `expect()` reports a demo that stops failing as an error.

The `/` makes `types` and `fn` [positional-only](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters),
so every keyword argument goes to `fn`.
[`**P`](14_Techniques--Decorators.md#p-and-r-keep-the-static-interface)
gives `*args` and `**kwargs` the parameter types of `fn`'s signature,
so the type checker verifies the forwarded arguments as if you had called `fn`:

```python
# demo_expect.py
import json
from exceptions import expect

def parse(text: str, *, base: int = 10) -> int:
    return int(text, base)

expect(ValueError, parse, "ff")
#: [ValueError] invalid literal for int() with base 10: 'ff'
expect((ValueError, TypeError), parse, "ff", base=1)  # [1]
#: [ValueError] int() base must be >= 2 and <= 36, or 0
expect(json.JSONDecodeError, json.loads, "{bad")  # [2]
#: [JSONDecodeError] Expecting property name enclosed in
#: double quotes: line 1 column 2 (char 1)
```

The call at `[1]` names two types in a tuple and forwards `base=1` as a keyword,
which `parse()` passes on to `int()`.
The message from `[2]` is too long for one line, so it wraps.

`aexpect()` is the `async` form,
for a coroutine function whose failure is the demonstration.

Where a demonstration needs several statements or an assignment in the guarded block,
`expected` remains the right tool.
`expect()` covers the common case of one call.

## Context Manager as Decorator

A context manager brackets a block of statements,
with setup before and cleanup after.
A typical [decorator](14_Techniques--Decorators.md)
brackets a function call the same way.
`contextlib.ContextDecorator` connects the two.
A subclass works both as a context manager and as a decorator.
Every manager `@contextmanager` produces inherits from `ContextDecorator`,
so `banner` works as a decorator,
although `ContextDecorator` is absent from the listing below:

```python
# context_decorator.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def banner(title: str) -> Generator[None]:
    print(f"=== {title} ===")
    try:
        yield
    finally:
        print(f"=== {title} ends ===")

@banner("quarterly")
def quarterly() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    quarterly()
    with banner("meeting"):
        print("agenda")
#: === quarterly ===
#: quarterly numbers
#: === quarterly ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
```

`ContextDecorator` applies [`functools.wraps`](14_Techniques--Decorators.md#wraps-keeps-the-runtime-interface),
so `quarterly()` keeps its name and docstring.

In `@banner("quarterly")`, the call constructs the manager,
which then decorates the function.
Written bare, `@banner` passes the function `quarterly` as `title`,
so the name `quarterly` holds a manager object rather than a function.
Calling `quarterly()` then raises a `TypeError`.
The type checker flags the decorator line.

Each call of the decorated function builds a fresh manager,
so `quarterly()` can run any number of times, each with its own enter and exit.
The single-use caution from `trace_gen.py` still holds for the manager object you specify in a `with`.

```python
# banner_cm.py
from contextlib import ContextDecorator

class banner(ContextDecorator):
    def __init__(self, title: str) -> None:
        self.title = title

    def __enter__(self) -> None:
        print(f"=== {self.title} ===")

    def __exit__(self, *exc: object) -> None:
        print(f"=== {self.title} ends ===")

@banner("quarterly")
def quarterly() -> None:
    print("quarterly numbers")

if __name__ == "__main__":
    quarterly()
    with banner("meeting"):
        print("agenda")
#: === quarterly ===
#: quarterly numbers
#: === quarterly ends ===
#: === meeting ===
#: agenda
#: === meeting ends ===
```

Like `suppress` and `expected`,
the class version of `banner` uses a lowercase name because you use it like a function.
Its `__exit__()` prints the closing banner however the block ended,
so it takes the `*exc: object` form and returns `None`,
which lets an exception from `quarterly()` propagate.

Unlike the generator form,
the class form re-enters the same instance on every call to `quarterly()`,
so every call shares any state the instance holds.

`banner`'s wrapper comes from `ContextDecorator`,
as the base class in `banner_cm.py` or by way of `@contextmanager` in `context_decorator.py`.
That wrapper always calls the function once, unchanged,
with setup before it and cleanup after.
So `banner` receives neither the arguments nor the return value of `quarterly()`,
and it cannot skip the call.
A hand-written decorator can do all three,
because it defines its own wrapper function.
[`repeat`](14_Techniques--Decorators.md#decorators-that-take-arguments)
forwards `*args` and `**kwargs` and returns the wrapped function's result.
[`hijack`](14_Techniques--Decorators.md#what-at-does)
returns a replacement that runs instead of the original function,
skipping its call.

`banner` offers one definition,
usable both as a `with` block and as a `@` decorator.
Use `ContextDecorator` when setup and cleanup should be identical on every call.

The wrapper treats a generator function differently.
Before Python 3.15, it wrapped only the call that creates the generator object,
so the context entered and exited before the generator's body ran.
The manager closed any resource it opened before the body could use it.
On 3.15 the wrapper enters the context at the first `next()` and exits it when the generator finishes or its `close()` method runs.
Decorating a generator with `banner` from `context_decorator.py` shows when the context opens and closes:

```python
# decorated_generator.py
from collections.abc import Iterator
from context_decorator import banner

@banner("rows")
def rows() -> Iterator[int]:
    for n in range(3):
        print(f"yield {n}")
        yield n

gen = rows()
print("created")
#: created
for row in gen:
    print(f"got {row}")
#: === rows ===
#: yield 0
#: got 0
#: yield 1
#: got 1
#: yield 2
#: got 2
#: === rows ends ===
print("done")
#: done
```

`created` prints before the opening banner,
because calling `rows()` builds the generator object.
The banner opens when the `for` loop calls `next()` for the first value.
The context stays open while the generator pauses at each `yield`,
so the loop's own `got` lines print inside the banner.

Before 3.15, both banner lines printed before `created`.
Code written for those versions leaves the decorator off and puts a `with` inside the generator around its body,
which works on every version.

## Combining Context Managers

A single `with` can include several managers, separated by commas.
Python 3.1 added that form as shorthand for one `with` nested inside another.
The managers enter left to right and exit in reverse:

```python
# multiple.py
from collections.abc import Generator
from contextlib import contextmanager

@contextmanager
def tag(name: str) -> Generator[str]:
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")

if __name__ == "__main__":
    with tag("ul") as outer, tag("li") as inner:
        print(f"  {outer} then {inner}")
#: <ul>
#: <li>
#:   ul then li
#: </li>
#: </ul>
```

When the managers are too long for one line, parentheses group them,
and the managers still enter left to right and exit in reverse:

    with (tag("ul") as outer,
          tag("li") as inner):
        ...

Python 3.10 added the parenthesized form.
Before it, a `with` too long for one line continued with a backslash.

When the number of managers depends on data available at runtime,
`contextlib.ExitStack` holds a dynamic set of managers and unwinds them in reverse when the block ends:

```python
# exit_stack.py
from contextlib import ExitStack
from multiple import tag

def wrap(names: list[str]) -> None:
    with ExitStack() as stack:
        open_tags = [
            stack.enter_context(tag(n)) for n in names]
        print("using", open_tags)

if __name__ == "__main__":
    wrap(["a", "b"])
    wrap(["a", "b", "c"])
#: <a>
#: <b>
#: using ['a', 'b']
#: </b>
#: </a>
#: <a>
#: <b>
#: <c>
#: using ['a', 'b', 'c']
#: </c>
#: </b>
#: </a>
```

The main guard in `multiple.py` keeps that listing's demo from running on import.

`wrap()` enters one manager per name in `names`,
so it learns the count at runtime.
A comma-separated `with` sets its count when you write it.

`wrap()` shows the case where every entry succeeds.
`ExitStack` makes a second guarantee, for a later entry that fails:
the stack unwinds the managers that entered earlier.

```python
# exit_stack_fails.py
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from exceptions import expected
from multiple import tag

@contextmanager
def broken(name: str) -> Generator[str]:
    print(f"<{name}>")
    raise RuntimeError(f"{name} failed to open")
    yield name

with expected(RuntimeError):
    with ExitStack() as stack:
        stack.enter_context(tag("a"))
        stack.enter_context(tag("b"))
        stack.enter_context(broken("c"))
#: <a>
#: <b>
#: <c>
#: </b>
#: </a>
#: [RuntimeError] c failed to open
```

`broken()` raises a `RuntimeError` before its `yield` and so fails to enter.
`ExitStack` registers a manager's exit after its `__enter__()` returns,
so it registers nothing for `broken("c")`.
The managers for `a` and `b` enter first,
so the stack holds both exits and unwinds them in reverse.
A comma-separated `with` follows the same rule.

## The `contextlib` Toolkit

The `contextlib` module provides ready-made managers.
Choose these before writing your own `__enter__()` and `__exit__()`.

- `suppress(*exceptions)` suppresses the listed exceptions,
  as `expected` does for the types it lists,
  without `expected`'s printing or its catch-everything default.
- `closing(obj)` calls `obj.close()` on exit,
  for objects that have `close()` but are not context managers.
- `chdir(path)` changes the current working directory on entry and changes back to the previous one on exit.
- `ExitStack` manages a [dynamic or conditional set of managers](#combining-context-managers).
- `ContextDecorator` lets a context manager also work as a decorator,
  as `banner` shows.
- `nullcontext(value)` is a do-nothing manager whose `__enter__()` returns `value`,
  useful when a `with` is optional and one code path should cover it.

A function might write to a path it opens, to a stream the caller hands it,
or to standard output by default.
When it finishes, the function should close the file it opened and leave the caller's stream and standard output open.
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

Exiting a `nullcontext` leaves its object as it was,
so the same `with` block closes the file in the `Path` branch and keeps `sys.stdout` and the caller's stream open,
as the caller expects.

`chdir()` is a class manager like `Trace`,
a few lines long in the standard library's source.
Its `__enter__()` appends `os.getcwd()` to a list and calls `os.chdir()`.
Its `__exit__()` pops the saved directory off the list and changes back to it.

The list makes one `chdir` instance re-entrant.
A `with` nested inside another `with` on the same instance saves a second directory.
Each exit restores the directory that its own entry saved.
A `@contextmanager` version keeps the saved directory in a local variable and restores it in a `finally`.
Like every generator manager, it is single-use.

The working directory belongs to the whole process,
so a `chdir()` block in one thread changes how every thread resolves a relative path.
The class's docstring calls it a "Non thread-safe context manager" for that reason.

## The Async Protocol

`with` calls `__enter__()` and `__exit__()`.
`async with` calls `__aenter__()` and `__aexit__()` and awaits what they return,
so the setup and the cleanup can both await.
`contextlib.asynccontextmanager` builds such a manager from an async generator,
the same way `@contextmanager` builds the synchronous form:

```python
# async_manager.py
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

@asynccontextmanager
async def session(name: str) -> AsyncGenerator[str]:
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

`session()` is the generator form with `async` in front of it.
`asyncio.run()` starts the [event loop](19_Techniques--Concurrency.md)
those awaits need.

Ordering, the three exception arguments,
and suppression through a truthy return work the same way in the async form.
The Concurrency chapter uses `async with` throughout, for `asyncio.TaskGroup`,
locks, and semaphores.
Each of those is an object with the two `a`-prefixed methods.

The `contextlib` tools for combining, closing,
and decorating managers each have an async counterpart.
`AsyncExitStack` is the `ExitStack` equivalent for holding several async managers.
`aclosing(obj)` awaits `obj.aclose()` on exit,
the async counterpart of `closing()`.
Every manager `@asynccontextmanager` builds inherits from `AsyncContextDecorator`,
so it also decorates a coroutine function,
the way `banner` decorates `quarterly()`.

## An Object Pool

Some objects are slow to create or limited in number by a system outside the program:
database connections, worker processes, licensed sessions.
The *Object Pool* pattern creates a set number of these objects up front and lends them out.
Lending is the dangerous half.
Every borrower must return the object on every path out of their code,
including the exception path.
Each missed return removes an object from the pool for good.
Enough missed returns empty the pool, so the next borrower waits forever.
A context manager can return every borrowed object to the pool.
In Python, a pool is a queue plus a `@contextmanager` method:

```python
# object_pool.py
from collections.abc import Generator
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
    def lease(self) -> Generator[R]:
        item = self._available.get()
        try:
            yield item
        finally:
            self._available.put(item)

    def available(self) -> int:
        return self._available.qsize()
```

`Pool` is generic over the pooled type,
and it neither creates nor destroys anything.
Its job is holding the items between leases and lending them out.

```python
# pool_demo.py
from contextlib import suppress
from object_pool import Connection, Pool

pool = Pool(Connection(1), Connection(2))
with pool.lease() as conn:
    print(conn.query("SELECT name FROM users"))
    print("available during lease:", pool.available())
#: connection 1: SELECT name FROM users
#: available during lease: 1
print("available after lease:", pool.available())
#: available after lease: 2
with suppress(RuntimeError), pool.lease():
    raise RuntimeError("crash during query")
print("available after crash:", pool.available())
#: available after crash: 2
```

The `finally` in `lease()` still returns the connection,
so the count is back to two.

An object pool differs from [*Flyweight*](35_Patterns--Flyweight.md),
the pattern closest to it.
A flyweight is immutable and shared by everyone at once.
A pooled object is usually mutable or stateful,
so the pool lends it to one borrower at a time.
The lease exists to take it back.

### An Empty Pool Blocks the Borrower

The queue does more than store the idle items.
`Queue` is thread-safe.
Its `get()` blocks while the pool is empty,
so a borrower waits until another borrower's `with` block ends and returns an item to the queue.
When several threads share one pool, the queue limits concurrent use,
the way a real database connection pool does.
[Concurrency](19_Techniques--Concurrency.md) covers threads, locks,
and the queues that coordinate them.

That blocking is for threads.
In an `asyncio` program a blocking `get()` blocks the whole event loop,
so an async pool holds an `asyncio.Queue`, awaits its `get()`,
and builds `lease()` with `asynccontextmanager`.

Eight threads contend for the pool.

```python
# pool_contention.py
import threading
import time
from typing import Final
from object_pool import Connection, Pool

WORKERS: Final[int] = 8
ROUNDS: Final[int] = 200
pool = Pool(Connection(1), Connection(2))
lock = threading.Lock()
held = 0
peak = 0

def borrow() -> None:
    global held, peak
    for _ in range(ROUNDS):
        with pool.lease():
            with lock:
                held += 1
                peak = max(peak, held)
            time.sleep(0.000_001)
            with lock:
                held -= 1

workers = [threading.Thread(target=borrow)
           for _ in range(WORKERS)]
for worker in workers:
    worker.start()
for worker in workers:
    worker.join()
print("peak leases:", peak)
#: peak leases: 2
print("pool size after:", pool.available())
#: pool size after: 2
```

`held` counts the threads holding a lease.
`peak` records the highest count `held` reaches.
The `time.sleep()` keeps each lease open long enough for other threads to call `lease()`,
so both connections are out at once.
A thread that calls `lease()` while the pool is empty blocks in `get()` until another thread returns a connection.
If the pool held a connection for each of the eight threads,
all eight would hold a lease together and the peak would be eight.

`available()` is a snapshot for the demo, not a synchronization primitive.
`Queue.qsize()` becomes approximate when more than one thread is borrowing,
because another thread can lease or return between the count and its use.

### Testing the Lease

Three tests check what the lease guarantees:
the item leaves the pool and comes back,
it also comes back when the block raises an exception,
and the pool hands out the same object rather than a new one:

```python
# test_object_pool.py
import pytest
from object_pool import Connection, Pool

def test_lease_takes_then_returns() -> None:
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

def test_lease_hands_out_same_object() -> None:
    pool = Pool(Connection(1))
    with pool.lease() as first:
        pass
    with pool.lease() as second:
        assert second is first
```

### What the Skeleton Leaves Out

A production pool adds refinements to the `Pool` skeleton.
It might create items lazily on first demand,
validate an item before lending it out, or give `get()` a timeout,
so a borrower facing an empty pool gets a `queue.Empty` exception instead of waiting forever.

Those refinements all guard the pool's side.
The borrower's side has a mistake.
`Pool` lets a borrower keep a reference after the `with` block ends,
then use it after the pool has lent the object to another borrower.
The pool hands out the same object again, not a copy,
so a stale reference and the new borrower's object are one and the same:

```python
# leaked_lease.py
from object_pool import Connection, Pool

pool = Pool(Connection(1))
with pool.lease() as first:
    stale = first  # Escapes the block

with pool.lease() as second:
    print(stale is second)
    print(stale.query("late"))
#: True
#: connection 1: late
```

The assignment to `stale` stands for any place a borrower stores the reference,
such as an attribute or a list.
With no assignment, `first` is the stale reference too.
The `as` target binds in the surrounding scope,
so `first` still names the connection after its block ends.
`test_lease_hands_out_same_object()` relies on that binding when it compares `second` with `first`.

For a mutable pooled resource, a stale reference is the source of corruption.
Two borrowers each use one connection as if they held it alone.

Guarding against a stale reference takes a wrapper that invalidates the borrower's handle on exit.
The `Pool` skeleton leaves out that refinement along with the others.

Each refinement in this section is a change inside `lease()`.
The code that creates, validates, and invalidates items runs there,
before and after the `yield`, so every `with pool.lease()` stays the same.

## Choosing a Form

A setup and teardown pair used once, in one place,
is often clearest as a `try`/`finally` written inline.
Write a manager when you want the `with` syntax at the call site,
or when several places need the same setup and teardown.

Four forms give you a context manager, once you decide you want one.
Try them in this order.
Use a `contextlib` manager when one fits, since `suppress`, `closing`,
`nullcontext`, and `ExitStack` cover most of the managers people write themselves.
Otherwise write a generator with `@contextmanager`,
which is the shortest form that can express setup, teardown,
and a `try`/`finally` between them.
Write a class with `__enter__()` and `__exit__()` when the manager needs state beyond one setup and teardown,
methods beyond the two protocol ones, or reuse across several `with` statements.
A generator manager handles one setup, one teardown, and one entry.
Add `ContextDecorator` only when the same bracket should also wrap whole functions.

Whichever form you choose, the borrower's side contains two lines.
Every change you make later goes inside the manager.

## Exercises

Try each exercise before opening its [solution](../Solutions/15_Techniques--Context_Managers/).

1.  In `trace_cm.py`, nest a second `with Trace("C") as u:` block inside the body of the first `with Trace("A") as t:` block,
    with its own `print(f"inside {u.name}")`.
    Before running it, predict the order in which the six "enter"/"inside"/"exit" lines appear.
2.  In `demo_exceptions.py`,
    change `expected(ZeroDivisionError)` to `expected((ZeroDivisionError, TypeError))`,
    then raise a `TypeError` instead of dividing by zero,
    and confirm that `expected` catches and prints it too.
3.  Add a third manager to the `with` statement in `multiple.py`,
    `tag("li")` again for a second item,
    and confirm the exit order still reverses the entry order.
4.  In `test_object_pool.py`, add a test that leases both connections at once,
    entering a second `with pool.lease()` block inside the first,
    and confirms `pool.available()` reaches `0`.
5.  Stack `@banner("outer")` and `@banner("inner")` from `context_decorator.py` on a single function and predict the order of the four bracketing lines before running it.
6.  Write a context manager `ignore_missing` whose `__exit__()` suppresses `KeyError` and lets everything else through,
    without using `contextlib.suppress`.
    Test it with a block that raises a `KeyError` and a block that raises a `ValueError`.
7.  Rewrite `exit_stack.py` to take its names from `sys.argv[1:]`,
    run it with no arguments and with three,
    and confirm that with three names the close order reverses the open order,
    and that with none the program prints `using []` alone.
8.  Wrap the `yield` in `careless()` from `no_finally.py` in `try`/`finally`,
    with the `exit` line in the `finally`.
    Before running it, predict where `exit A` appears relative to `caught: boom`.
