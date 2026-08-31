# Error Handling: Solutions

## 1. A fourth step, `func_e()`, added to the `bind()` chain

```python
# exercise_1.py
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Ok[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        return self  # Pass the failure forward unchanged

type Result[A, E] = Ok[A] | Err[E]

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Err(f"func_a({i})")
    return Ok(i)

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Err(f"func_b({i})")
    return Ok(i)

def func_c(i: int) -> Result[int, str]:
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        return Err(f"func_c({i}): {e}")
    return Ok(i)

def func_e(i: int) -> Result[int, str]:
    if i == 4:
        return Err(f"func_e({i})")
    return Ok(i * 10)

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c).bind(func_e)

for i in range(5):
    print(i, composed(i))
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Err(error='func_b(2)')
#: 3 Err(error='func_c(3): division by zero')
#: 4 Err(error='func_e(4)')
```

Adding a fourth `.bind(func_e)` needed no change to `Result`, `Ok`,
or `Err`. `i == 4` reaches `func_e()` only because it survived
`func_a`, `func_b`, and `func_c` (unlike `1`, `2`, and `3`, which fail
earlier and never even reach `func_e`), and `func_e(4)`'s `Err`
then propagates unchanged through nothing further, since it is the
last step in the chain. Every input from `0` to `4` now fails at
exactly one step, which happens to be a different step each time,
demonstrating that a chain of any length short-circuits at its first
failure, wherever that falls.

## 2. `Err.map_error()`

```python
# exercise_2.py
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Ok[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

    def map_error(
        self, func: Callable[..., object]
    ) -> Ok[A]:
        return self  # An Ok has no error to transform

@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        return self

    def map_error[F](
        self, func: Callable[[E], F]
    ) -> Err[F]:
        return Err(func(self.error))

type Result[A, E] = Ok[A] | Err[E]

def prefix(msg: str) -> str:
    return f"error: {msg}"

print(Ok(5).map_error(prefix))
#: Ok(answer=5)
print(Err("boom").map_error(prefix))
#: Err(error='error: boom')
```

`map_error()` is `bind()`'s mirror image: `bind()` transforms the
success value and leaves a failure alone, while `map_error()`
transforms the failure value and leaves a success alone. `Ok`'s
version is a no-op, since there is no error to touch. `Err`'s
version applies `func` to `self.error` and wraps the result in a new
`Err`. Adding a prefix to every error in a chain is then one call,
`result.map_error(prefix)`, applied once at the boundary where the
error is reported, rather than threading the prefix through every
function that might produce one.

## 3. `combined()` that collects every failure

```python
# test_ch42_combined.py
from __future__ import annotations
from dataclasses import dataclass

# Concrete (non-generic): this exercise combines three
# ints into a str, so there is no type parameter to
# preserve, and isinstance() can narrow a concrete class
# without running into type erasure.
@dataclass(frozen=True)
class IntResult:
    value: int

@dataclass(frozen=True)
class ErrorResult:
    error: str

type Combining = IntResult | ErrorResult

@dataclass(frozen=True)
class MultiErrorResult:
    errors: list[str]

def func_a(i: int) -> Combining:
    if i == 1:
        return ErrorResult(f"func_a({i})")
    return IntResult(i)

def func_b(i: int) -> Combining:
    if i == 2:
        return ErrorResult(f"func_b({i})")
    return IntResult(i)

def func_c(i: int) -> Combining:
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        return ErrorResult(f"func_c({i}): {e}")
    return IntResult(i)

def add(a: int, b: int, c: int) -> str:
    return f"add({a} + {b} + {c}): {a + b + c}"

def combined(i: int, j: int) -> str | MultiErrorResult:
    result_a = func_a(i)
    result_b = func_b(j)
    result_c = func_c(i + j)
    errors = [r.error
              for r in (result_a, result_b, result_c)
              if isinstance(r, ErrorResult)]
    if errors:
        return MultiErrorResult(errors)
    assert isinstance(result_a, IntResult)
    assert isinstance(result_b, IntResult)
    assert isinstance(result_c, IntResult)
    return add(result_a.value, result_b.value,
               result_c.value)

def test_combined_collects_every_failure() -> None:
    assert combined(1, 2) == MultiErrorResult(
        ["func_a(1)", "func_b(2)",
         "func_c(3): division by zero"])

def test_combined_reports_single_failure() -> None:
    assert combined(1, 5) == MultiErrorResult(["func_a(1)"])

def test_combined_success_unchanged() -> None:
    assert combined(7, 5) == "add(7 + 5 + 12): 24"
```

Unlike the `bind()`-chained version, which stops at the first
failure it meets, this version calls all three functions
unconditionally and only inspects their results afterward, gathering
every `ErrorResult`'s `.error` into one list. `combined(1, 5)` now
reports a single-item list, `["func_a(1)"]`, because `func_b(5)` and
`func_c(6)` both succeed. `combined(1, 2)` reports all three failures
at once, since `i=1` fails `func_a`, `j=2` fails `func_b`, and
`i+j=3` fails `func_c`, none of which the short-circuiting `bind()`
chain could ever surface together. This trade-off, calling every step
regardless of earlier failures, only makes sense when the steps are
independent of each other's results, which is why `func_c` here takes
`i + j` rather than a value produced by `func_a` or `func_b`.

This version also trades away genericity on purpose. `func_a()`,
`func_b()`, and `func_c()` each need an intermediate result of "an
`int` or an error string" (`IntResult | ErrorResult`), while
`combined()` itself needs a different shape, "a finished `str` or a
list of error strings." Reusing one generic `Ok[A]`/`Err[E]`
pair for both asks a type checker to recover a type parameter
from a plain `isinstance()` check, which Python's runtime type
erasure makes impossible in general. `ty` reports that gap as
an error. Two small concrete classes sidestep the problem entirely,
since there is no parameter to lose.

## 4. `@safe(ValueError)`, catching only what you name

```python
# exercise_4.py
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Protocol, final

@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

@final
@dataclass(frozen=True)
class Err[E]:
    error: E

type Result[A, E] = Ok[A] | Err[E]

class SafeDecorator(Protocol):
    def __call__[**P, A](
        self, func: Callable[P, A]
    ) -> Callable[P, Result[A, Exception]]: ...

def safe(*catch: type[Exception]) -> SafeDecorator:
    def decorate[**P, A](
        func: Callable[P, A]
    ) -> Callable[P, Result[A, Exception]]:
        @wraps(func)
        def wrapper(
            *args: P.args, **kwargs: P.kwargs
        ) -> Result[A, Exception]:
            try:
                return Ok(func(*args, **kwargs))
            except catch as e:
                return Err(e)
        return wrapper
    return decorate

@safe(ValueError)
def parse(text: str) -> int:
    if not text.isdigit():
        raise TypeError(f"{text!r} is not digits")
    return int(text)

print(parse("42"))
#: Ok(answer=42)
try:
    parse("oops")
except TypeError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: TypeError: 'oops' is not digits
```

`safe()` gains a layer: it now takes the exception types and returns
the decorator, instead of being the decorator. The `except catch`
clause accepts the tuple directly, which is why the whole change is
one parameter and one word.

`parse("42")` still comes back as an `Ok`. `parse("oops")` raises a
`TypeError`, which is not in the caught tuple, so it propagates
through `wrapper` untouched and the caller sees an ordinary traceback.
Under the chapter's `@safe` it would have arrived as
`Err(TypeError(...))`, indistinguishable from a bad-input failure.

The `SafeDecorator` protocol is what keeps the types honest. `safe()`
returns a function that is itself generic over the function it
decorates, and there is no way to say that with a plain
`Callable[...]` annotation: the type parameters belong to the returned
callable, not to `safe()`. A protocol with a generic `__call__` says
exactly that, and it is why `parse` keeps the signature
`(str) -> Result[int, Exception]` rather than degrading to `Any`.

## 5. Notes that survive as data

```python
# exercise_5.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import final

@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

@final
@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        return self

type Result[A, E] = Ok[A] | Err[E]

def load_setting(name: str,
                 text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"setting {name!r} received {text!r}")
        return Err(e)

def report(result: Result[int, Exception]) -> None:
    match result:
        case Ok(answer):
            print(f"ok: {answer}")
        case Err(error):
            print(f"failed: {type(error).__name__}")
            for note in error.__notes__:
                print(f"  {note}")

report(load_setting("timeout", "30").bind(
    lambda _: load_setting("retries", "3")))
#: ok: 3
report(load_setting("timeout", "soon").bind(
    lambda _: load_setting("retries", "3")))
#: failed: ValueError
#:   setting 'timeout' received 'soon'
report(load_setting("timeout", "30").bind(
    lambda _: load_setting("retries", "many")))
#: failed: ValueError
#:   setting 'retries' received 'many'
```

Each failure reports the setting that caused it, and the second and
third runs differ only in which name appears in the note. The note
travels inside the `Err` as ordinary data, so `report()` can print it
long after the frame that knew the setting name has returned. Nothing
is reconstructed from a traceback, because there is no traceback.

The answer to the question is that there is no note to lose. A
successful `load_setting()` never enters the `except` branch, so it
never calls `add_note()`, and an `Ok` carries no exception to hang a
note on. Notes attach to exceptions, so only the failing path has
one, which is the reason the failing path is the only one that needs
to explain itself.

The lambdas ignore their parameter, since the second setting does not
depend on the first one's value. That is the case `bind()` reads worst
for: it exists to thread an answer forward, and here there is no
answer to thread, only an ordering. This is where the do-notation
mentioned in [The returns Library](../Chapters/42_Functional--Error_Handling.md#the-returns-library)
reads better than nested binds.

## 6. `int | None` collapses the three failures into one

```python
# exercise_6.py
def func_a(i: int) -> int | None:
    if i == 1:
        return None
    return i

def func_b(i: int) -> int | None:
    if i == 2:
        return None
    return i

def func_c(i: int) -> int | None:
    try:
        1 / (i - 3)
    except ZeroDivisionError:
        return None
    return i

def composed(i: int) -> int | None:
    a = func_a(i)
    if a is None:
        return None
    b = func_b(a)
    if b is None:
        return None
    return func_c(b)

for i in range(5):
    print(i, composed(i))
#: 0 0
#: 1 None
#: 2 None
#: 3 None
#: 4 4
```

The caller can tell apart nothing at all. Inputs `1`, `2`, and `3`
fail in three different functions for three different reasons, and
all three arrive as the same `None`. Compare the `Result` version,
where the same three inputs report `func_a(1)`, `func_b(2)`, and
`func_c(3): division by zero`.

The structure of `composed()` barely changed: `if a is None` replaced
`if isinstance(a, Err)`, and the early returns stayed. What changed is
what survives the return. `None` is a single value with no room to
carry a reason, so every failure that reaches it becomes the same
failure. This is the trade the chapter names: use `| None` when
absence is the whole story, and a `Result` when the caller may need to
act on which failure occurred, or when a person reading a bug report
needs to know which of three steps went wrong.
