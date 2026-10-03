# Error Handling: Solutions

## 1. A fourth step, `func_d()`, added to the `bind()` chain

> Add a `func_d()` that returns a `Result[int, str]`,
> and extend the `bind()` chain in `composing_with_bind.py` to include it.
> Put it in the middle of the chain rather than at the end,
> so an `Err` from it has a later step to skip,
> and confirm that the step never runs.

<details>
<summary>Where to look</summary>

[Composing With bind](../../Chapters/42_Functional--Error_Handling.md#composing-with-bind) chains steps so that an `Err` skips every step after it.
Write `func_d()` with the same `Result[int, str]` signature, and add one more `.bind()` before the last step.
To see that the skipped step never runs, give it a side effect such as a `print()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from result import Err, Ok, Result

def func_a(i: int) -> Result[int, str]:
    ...

def func_b(i: int) -> Result[int, str]:
    ...

def func_c(i: int) -> Result[int, str]:
    ...

def func_d(i: int) -> Result[int, str]:
    ...

def composed(i: int) -> Result[int, str]:
    ...
```

<details>
<summary>Solution</summary>

If you append `func_d()` at the end of the chain,
an `Err` from it has no later step to skip:
input `4` prints `func_c(4) runs` and then `Err(error='func_d(4)')`,
so the run cannot show that a failure from the new step stops the chain.
The solution puts `func_d()` before `func_c()`,
whose printed line then goes missing for `4`.

```python
# exercise_1.py
from result import Err, Ok, Result

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Err(f"func_a({i})")
    return Ok(i)

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Err(f"func_b({i})")
    return Ok(i)

def func_c(i: int) -> Result[int, str]:
    print(f"func_c({i}) runs")
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        return Err(f"func_c({i}): {e}")
    return Ok(i)

def func_d(i: int) -> Result[int, str]:
    if i == 4:
        return Err(f"func_d({i})")
    return Ok(i)

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_d).bind(func_c)

for i in range(5):
    print(i, composed(i))
#: func_c(0) runs
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Err(error='func_b(2)')
#: func_c(3) runs
#: 3 Err(error='func_c(3): division by zero')
#: 4 Err(error='func_d(4)')
```

**Insert the new step.** `Result` comes from the chapter's `utils/result.py`: adding a fourth
`.bind(func_d)` needs no change to `Result`, `Ok`, or `Err`.
`func_d()` sits before `func_c()` in the chain, so an `Err` from
`func_d()` has a later step to skip.

**Make the skipped step visible.** `func_c()` prints a line when it runs, and
that line is the confirmation: it appears for `0` and `3` and is
missing for `4`. `4` reaches `func_d()` because it survives
`func_a()` and `func_b()`, and the `Err` that comes back travels to
the end of the chain untouched: `Err.bind()` returns `self` without
calling `func_c()`.

`1` and `2` fail earlier and stop the chain
before `func_d()` sees them, and `3` passes through `func_d()`
unchanged to fail in `func_c()`, so inputs `1` through `4` each fail
at a different step. A chain short-circuits at its first failure,
wherever that falls, and the order of the steps decides where the
chain stops.

</details>
</details>
</details>

## 2. `Err.map_error()`

> Give `Err` a `map_error()` method that transforms the error it holds,
> leaving an `Ok` untouched
> (for chains to keep working, `Ok` needs its own `map_error()` that returns `self`).
> Use it to add a prefix to every error.

<details>
<summary>Where to look</summary>

[A Result Type](../../Chapters/42_Functional--Error_Handling.md#a-result-type) defines `Ok` and `Err` with a `bind()` on each, and `map_error()` is the mirror image of that split.
`Err` applies the function to its error and wraps the return value in a new `Err`.
`Ok` returns `self`, so a chain can call `map_error()` without checking which side it holds.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Callable
from typing import final
from record import record

@final
@record
class Ok[A]:
    answer: A

    def unwrap(self) -> A:
        ...

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        ...

    def map_error(
        self, func: Callable[..., object]
    ) -> Ok[A]:
        ...

@final
@record
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        ...

    def map_error[F](
        self, func: Callable[[E], F]
    ) -> Err[F]:
        ...

type Result[A, E] = Ok[A] | Err[E]

def prefix(msg: str) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you give `map_error()` to `Err` alone,
`Ok(5).map_error(prefix)` raises an `AttributeError`: `'Ok' object has no attribute 'map_error'`.
On a value typed `Result[int, str]`, `ty` reports `unresolved-attribute` for every `map_error()` call,
including one on a value that holds an `Err`,
because the `Ok` member of the union has no such method.
The solution gives `Ok` a `map_error()` that returns `self`,
so a chain can call the method without checking which side it holds.

```python
# exercise_2.py
from collections.abc import Callable
from typing import final
from record import record

@final
@record
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

@final
@record
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

This exercise changes `Ok` and `Err`, so the listing defines its own
pair and does not import the chapter's. `map_error()` works on the
side `bind()` skips: `bind()` passes a success to the next step and
leaves a failure alone, while `map_error()` transforms the failure
and leaves a success alone. `map_error()` differs from `bind()` in
what it asks of `func`. `bind()`'s function returns a `Result`; `map_error()`'s
function returns the new error, and `map_error()` wraps it, the way
the chapter's `map()` wraps a new answer. The `returns` library names
this method `alt()`.

**Leave a success alone.** `Ok`'s version is a no-op, since there is no
error to touch.

**Transform the failure.** `Err`'s version applies `func` to `self.error` and
wraps `func`'s return value in a new `Err`.

**Prefix errors at the boundary.** Adding a prefix to every error in a chain is then one call,
`result.map_error(prefix)`, applied once at the boundary where you
report the error, rather than threading the prefix through every
function that might produce one.

</details>
</details>
</details>

## 3. `combined()` that collects every failure

> Rewrite `combined()` so it collects all the failures instead of stopping at the first one,
> returning `Result[str, list[str]]`.
> Write the tests first.

<details>
<summary>Where to look</summary>

[Combining Multiple Results](../../Chapters/42_Functional--Error_Handling.md#combining-multiple-results) stops at the first `Err` because each step depends on the one before.
Here the three calls are independent, so call all of them first and keep the results.
Gather the `.error` of each `Err` into a list, return `Err(errors)` when the list is not empty, and write the three tests before the function.

<details>
<summary>Solution</summary>

If you keep the nested `bind()` calls from `combining.py`,
`combined(1, 2)` returns `Err(error='func_a(1)')`:
the chain stops at the first failure,
so the failures from `func_b(2)` and `func_c(3)` never reach the caller,
and the first test fails.
The three calls are independent,
so the solution makes all three before it inspects any result.

```python
# test_ch42_combined.py
from result import Err, Ok, Result

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

def add(a: int, b: int, c: int) -> str:
    return f"add({a} + {b} + {c}): {a + b + c}"

def combined(i: int, j: int) -> Result[str, list[str]]:
    a, b, c = func_a(i), func_b(j), func_c(i + j)
    errors = [r.error for r in (a, b, c)
              if isinstance(r, Err)]
    if errors:
        return Err(errors)
    assert isinstance(a, Ok)
    assert isinstance(b, Ok)
    assert isinstance(c, Ok)
    return Ok(add(a.answer, b.answer, c.answer))

def test_combined_collects_every_failure() -> None:
    assert combined(1, 2) == Err(
        ["func_a(1)", "func_b(2)",
         "func_c(3): division by zero"])

def test_combined_reports_single_failure() -> None:
    assert combined(1, 5) == Err(["func_a(1)"])

def test_combined_success_unchanged() -> None:
    assert combined(7, 5) == Ok("add(7 + 5 + 12): 24")
```

**Call every step.** Unlike the `bind()`-chained version, which stops at the first
failure it meets, this version calls all three functions
unconditionally. Calling every step regardless
of earlier failures makes sense only when the steps are independent
of each other's results. That independence is why `func_c` here takes
`i + j` rather than a value produced by `func_a` or `func_b`.

**Gather the failures.** `combined()` then inspects the three results, gathering
every `Err`'s `.error` into one list. `combined(1, 5)` now
reports a single-item list, `["func_a(1)"]`, because `func_b(5)` and
`func_c(6)` both succeed. `combined(1, 2)` reports all three failures
at once: `i=1` fails `func_a`, `j=2` fails `func_b`, and `i+j=3`
fails `func_c`. The short-circuiting `bind()` chain could never
surface those three failures together.

**Widen the error channel.** One generic pair carries both shapes. The three steps return
`Result[int, str]`, an `int` or one error string, while `combined()`
returns `Result[str, list[str]]`, a finished `str` or a list of error strings.
`Ok` and `Err` take whatever type parameters each call needs, so the
error channel widening from `str` to `list[str]` costs no new classes.

**Narrow for the type checker.** The type checker follows the widening: `isinstance(r, Err)` narrows the comprehension to
`list[str]`, and the three `assert isinstance` lines narrow each
success to `Ok[int]` so `.answer` is an `int`. The asserts document
what the `if errors:` return has already established, since a checker
cannot see that an empty error list means all three succeeded.

</details>
</details>

## 4. `@safe(ValueError)`, catching only what you name

> Change `@safe` so it takes the exception types it should catch,
> as in `@safe(ValueError)`, and lets anything else propagate.
> Show that a `TypeError` raised inside the wrapped function now propagates,
> and `@safe` no longer returns it as an `Err`.

<details>
<summary>Where to look</summary>

[Turning Exceptions into Results](../../Chapters/42_Functional--Error_Handling.md#turning-exceptions-into-results) shows `@safe` as a decorator that catches every exception.
To take arguments, `safe()` becomes a function that receives the exception types and returns the decorator.
An `except` clause accepts a tuple of exception types, so the wrapper changes very little.
A `Protocol` with a generic `__call__` keeps the decorated function's signature precise.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections.abc import Callable
from functools import wraps
from typing import Protocol
from exceptions import expect
from result import Err, Ok, Result

class SafeDecorator(Protocol):
    def __call__[**P, A](
        self, func: Callable[P, A]
    ) -> Callable[P, Result[A, Exception]]: ...

def safe(*catch: type[Exception]) -> SafeDecorator:
    ...

@safe(ValueError)
def parse(text: str) -> int:
    ...
```

<details>
<summary>Solution</summary>

If you pass the exception type to the chapter's one-layer `safe()`,
`@safe(ValueError)` wraps `ValueError` as if it were the function.
Python then calls that wrapper with `parse()` as its argument,
so `parse` names an `Ok` holding a `ValueError`,
and `parse("42")` raises a `TypeError`, `'Ok' object is not callable`
(`ty` reports `call-non-callable` at the same call).
The solution adds an outer layer:
`safe(ValueError)` returns the decorator, and the decorator wraps `parse()`.

```python
# exercise_4.py
from collections.abc import Callable
from functools import wraps
from typing import Protocol
from exceptions import expect
from result import Err, Ok, Result

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
expect(TypeError, parse, "oops")
#: [TypeError] 'oops' is not digits
```

**Type the returned decorator.** `safe()`
returns a decorator that is generic over the function it
decorates. The `SafeDecorator` protocol says that with a generic `__call__`,
so `parse` keeps the signature `(text: str) -> Result[int, Exception]`.
A nested `Callable` annotation types `parse` as precisely.
If `safe()` declares `[**P, A]` and returns
`Callable[[Callable[P, A]], Callable[P, Result[A, Exception]]]`,
`ty` reveals `parse` as `(text: str) -> Ok[int] | Err[Exception]`,
and one `safe(ValueError)` decorator stays generic across two different functions.
The protocol is a readability choice:
it gives the decorator's shape a name,
so `safe()`'s return annotation reads `SafeDecorator`
and the revealed signature keeps the `Result` alias.

**Accept the types to catch.** `safe()` gains a layer: it now takes the exception types and returns
the decorator, instead of being the decorator.

**Catch only the named types.** The `except catch`
clause accepts the tuple directly, so `wrapper` itself changes by
one word.

**Let everything else propagate.** `parse("42")` still comes back as an `Ok`. `parse("oops")` raises a
`TypeError`, which `@safe(ValueError)` never catches, so the
`TypeError` propagates through `wrapper` untouched. `expect()`
catches it outside `parse()` and prints it; without that catch the
caller sees an ordinary traceback. Under the chapter's `@safe` that same
`TypeError` arrives as `Err(TypeError(...))`, indistinguishable from
a bad-input failure.

</details>
</details>
</details>

## 5. Notes that survive as data

> Write `load_setting(name, text)` that returns `Result[int, Exception]` and attaches a note naming the setting.
> Chain two of them with `bind()` and print the notes from whichever one failed.
> Does the successful call carry a note?
> Why or why not?

<details>
<summary>Where to look</summary>

[Attaching Context to an Exception](../../Chapters/42_Functional--Error_Handling.md#attaching-context-to-an-exception) shows `add_note()` and the `__notes__` list it fills.
Call `add_note()` in the `except` clause before wrapping the exception in an `Err`.
A `match` on the `Result` reads the notes back from the error.
To answer the question, look at which code path reaches `add_note()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from result import Err, Ok, Result

def load_setting(name: str,
                 text: str) -> Result[int, Exception]:
    ...

def report(result: Result[int, Exception]) -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from result import Err, Ok, Result

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

**Note only the failing path.** The successful call has no note to lose. A successful
`load_setting()` returns from inside the `try` block, so it never
reaches `add_note()`, and an `Ok` carries no exception to hang a
note on. Notes attach to exceptions, so only the failing path
carries one, and only the failing path has anything to explain.

**Report without a traceback.** Each failure reports the setting that caused it, and the second and
third runs differ only in which name appears in the note. The note
travels inside the `Err` as ordinary data, so `report()` can print
it long after the frame that knew the setting name has returned.
`report()` reconstructs nothing from a traceback, because nothing
prints one: the exception still holds its `__traceback__`, and the
exception does not propagate to a handler that would show it.

**Sequence the two loads.** The lambdas ignore their parameter, since the second setting does not
depend on the first one's value. `bind()` reads worst in that case:
it exists to pass an answer forward, and here it passes an ordering
and the lambda discards the answer. The do-notation mentioned
in [The returns Library](../../Chapters/42_Functional--Error_Handling.md#the-returns-library)
reads better here.

</details>
</details>
</details>

## 6. `int | None` collapses the three failures into one

> Rewrite `func_a()`, `func_b()`,
> and `func_c()` to return `int | None` instead of `Result[int, str]`,
> and adjust `composing.py` to match.
> What can the caller still tell about which of the three steps failed?

<details>
<summary>Where to look</summary>

[Which Failures Get a Result](../../Chapters/42_Functional--Error_Handling.md#which-failures-get-a-result) compares `None` with `Result`, and [Composing by Hand](../../Chapters/42_Functional--Error_Handling.md#composing-by-hand) has the chain to adapt.
Return `None` where each function returned an `Err`, and replace each `isinstance` test with `is None`.
Then compare the outputs for inputs `1`, `2`, and `3` with the `Result` version.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
def func_a(i: int) -> int | None:
    ...

def func_b(i: int) -> int | None:
    ...

def func_c(i: int) -> int | None:
    ...

def composed(i: int) -> int | None:
    ...
```

<details>
<summary>Solution</summary>

If you test with `if not a:` and `if not b:` instead of `is None`,
input `0` prints `0 None`.
`func_a(0)` succeeds with `0`, which is falsy,
so `composed()` treats a success as a failure,
and the type checker accepts that version.
The solution compares with `is None`, which separates a missing value from a zero.

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

All three failures have collapsed into each other. Inputs `1`, `2`,
and `3` fail in three different functions for three different
reasons, and all three arrive as the same `None`. Compare the
`Result` version, where the same three inputs report `func_a(1)`,
`func_b(2)`, and `func_c(3): division by zero`.

**Stop at the first failure.** The structure of `composed()` barely changes: `if a is None` replaces
`if isinstance(a, Err)`, and the early returns stay. What changes is
what survives the return. `None` is a single value with no room to
carry a reason, so every failure that reaches it becomes the same
failure.

The chapter weighs `None` against `Result`. Use `| None` when absence
needs no explanation. Use a `Result` when the caller may need to act on
which failure occurred, or when a person reading a bug report needs
to know which of three steps went wrong.

</details>
</details>
</details>
