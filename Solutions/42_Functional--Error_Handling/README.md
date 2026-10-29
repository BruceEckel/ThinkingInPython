# Error Handling: Solutions

## 1. A fourth step, `func_d()`, added to the `bind()` chain

> Add a `func_d()` that returns a `Result[int, str]`,
> and extend the `bind()` chain in `composing_with_bind.py` to include it.
> Put it in the middle of the chain rather than at the end,
> so an `Err` from it has a later step to skip,
> and confirm that the later step does not run.

<details>
<summary>Where to look</summary>

[Composing With bind](../../Chapters/42_Functional--Error_Handling.md#composing-with-bind)
chains steps so that an `Err` skips every step after it.
Write `func_d()` with the same `Result[int, str]` signature,
and add one more `.bind()` before the last step.
To see whether the later step runs, give it a side effect such as a `print()`.

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
<summary>Done when</summary>

for the input that `func_d()` rejects,
your run prints the `Err` from `func_d()` and the later step's trace line is missing,
while every input that passes `func_d()` still prints that line.
The other inputs give the same results as `composing_with_bind.py`.

<details>
<summary>Solution</summary>

If you append `func_d()` at the end of the chain,
an `Err` from it comes after every other step has run.
Input `4` prints `func_c(4) runs` and then `Err(error='func_d(4)')`,
so the run cannot show that a failure from the new step stops the chain.
The solution puts `func_d()` before `func_c()`,
so the run for `4` stops before `func_c()` prints its line.

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

**Insert the new step.**
Adding a third `.bind()`, for `func_d()`, leaves `Result`, `Ok`,
and `Err` as they are,
so the listing imports them from the chapter's `utils/result.py`.
Because `func_d()` sits before `func_c()` in the chain,
an `Err` from `func_d()` has a later step to skip.

**Make the skipped step visible.**
`func_c()`'s trace line appears for `0` and `3` and is missing for `4`,
which confirms the skip.
`func_d(4)` returns an `Err`,
and `Err.bind()` returns `self` without calling `func_c()`,
so that `Err` is the chain's result.

A chain short-circuits at the first step that fails,
so the order of the steps decides where the chain stops.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. `Err.map_error()`

> Give `Err` a `map_error()` method that transforms the error it holds,
> leaving an `Ok` as it is
> (for chains to keep working, `Ok` needs its own `map_error()` that returns `self`).
> Use it to add a prefix to every error.

<details>
<summary>Where to look</summary>

[A Result Type](../../Chapters/42_Functional--Error_Handling.md#a-result-type)
defines `Ok` and `Err` with a `bind()` on each.
`map_error()` is the mirror image of those two `bind()` methods.
`Err` applies the function to its error and wraps the return value in a new `Err`.
`Ok` returns `self`, so a chain can call `map_error()` whichever side it holds.

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
<summary>Done when</summary>

`Err("boom").map_error(prefix)` prints an `Err` holding the prefixed message,
`Ok(5).map_error(prefix)` prints `Ok(answer=5)` unchanged,
and `uv run ty check` passes on a `map_error()` call on a parameter annotated `Result[int, str]`.
If `Ok` lacks the method, that call draws `unresolved-attribute`.

<details>
<summary>Solution</summary>

If you give `map_error()` to `Err` alone,
`Ok(5).map_error(prefix)` raises an `AttributeError`:
`'Ok' object has no attribute 'map_error'`.
On a value typed `Result[int, str]`,
`ty` reports `unresolved-attribute` for every `map_error()` call,
including one on a value that holds an `Err`,
because the `Ok` member of the union has no such method.
The solution gives `Ok` a `map_error()` that returns `self`,
so a chain can call the method whichever side it holds.

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

This exercise changes `Ok` and `Err`,
so the listing defines its own pair instead of importing the chapter's pair.

`map_error()` works on the side `bind()` skips.
`bind()` passes a success to the next step and leaves a failure alone,
while `map_error()` transforms the failure and leaves a success alone.

`map_error()` differs from `bind()` in what it asks of `func`.
`bind()`'s function returns a `Result`.
`map_error()`'s function returns the new error,
and `map_error()` wraps it in an `Err`.

The `returns` library has a method on each side.
Its [`map()`](../../Chapters/42_Functional--Error_Handling.md#composing-with-bind)
wraps a new answer the way `map_error()` wraps a new error,
and its counterpart to `map_error()` is `alt()`.

**Leave a success alone.**
`Ok`'s version returns `self`,
because an `Ok` holds an answer and `func` transforms errors.

**Transform the failure.**
`Err`'s version builds a new `Err` because `func` can change the error's type,
from `E` to `F`.

**Prefix errors at the boundary.**
To prefix every error in a chain, you call `result.map_error(prefix)` once,
at the boundary where you report the error.
The functions that might produce an error leave the prefix to that one call.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. `combined()` that collects every failure

> Rewrite `combined()` so it collects all the failures instead of stopping at the first one,
> returning `Result[str, list[str]]`.
> Write the tests first.

<details>
<summary>Where to look</summary>

[Combining Multiple Results](../../Chapters/42_Functional--Error_Handling.md#combining-multiple-results)
stops at the first `Err` because each nested `bind()` short-circuits.
The three calls take independent inputs, so `combined()` can make all three.
Call all three first, then `match` on the three results together.
One `case` takes three `Ok`s,
and any other combination gathers the `.error` of each `Err` into a list.
Write the three tests before the function.

<details>
<summary>Done when</summary>

your tests pass and check three calls:
`combined(1, 2)` returns an `Err` listing all three failures in step order,
`combined(1, 5)` an `Err` holding `["func_a(1)"]` alone,
and `combined(7, 5)` the same `Ok(answer='add(7 + 5 + 12): 24')` that `combining.py` prints.
`uv run ty check` passes with no `assert` in `combined()`.

<details>
<summary>Solution</summary>

If you keep the nested `bind()` calls from `combining.py`,
`combined(1, 2)` returns `Err(error='func_a(1)')`.
The chain stops at the first failure, before `func_b(2)` and `func_c(3)`,
so the result holds one error where the first test expects three.
Because the three calls are independent,
the solution makes all three before it inspects any result.

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
    match func_a(i), func_b(j), func_c(i + j):
        case Ok(a), Ok(b), Ok(c):
            return Ok(add(a, b, c))
        case results:
            return Err([r.error for r in results
                        if isinstance(r, Err)])

def test_combined_collects_every_failure() -> None:
    assert combined(1, 2) == Err(
        ["func_a(1)", "func_b(2)",
         "func_c(3): division by zero"])

def test_combined_reports_single_failure() -> None:
    assert combined(1, 5) == Err(["func_a(1)"])

def test_combined_success_unchanged() -> None:
    assert combined(7, 5) == Ok("add(7 + 5 + 12): 24")
```

**Call every step.**
The `bind()`-chained version stops at the first failure,
while this version calls all three functions every time.
Calling every step after a failure makes sense only when each step's input comes from the caller.
So `func_c()` here takes `i + j`, built from the caller's arguments,
rather than a value that `func_a()` or `func_b()` produces.

**Gather the failures.**
`case Ok(a), Ok(b), Ok(c)` takes the all-`Ok` combination,
so every tuple that reaches `case results` holds at least one `Err` and produces an error list with at least one entry.

**Widen the error type.**
The three steps return `Result[int, str]`, an `int` or one error string,
while `combined()` returns `Result[str, list[str]]`,
a finished `str` or a list of error strings.
One generic `Ok`/`Err` pair carries both shapes,
because `Ok` and `Err` take the type parameters each call needs.

**Narrow for the type checker.**
The type checker verifies both instantiations.
The `Ok(a), Ok(b), Ok(c)` pattern narrows each result to `Ok[int]`, so `a`, `b`,
and `c` are `int`s.
`isinstance(r, Err)` narrows each `r` to `Err[str]`,
so the comprehension builds a `list[str]`.

If you build the error list first and return early when it holds anything,
the type checker rejects a later `a.answer`.
It cannot infer that an empty error list means all three succeeded.
The tuple pattern states that condition in the `case`,
where the type checker reads it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. `@safe(ValueError)`, catching only what you name

> Change `@safe` so it takes the exception types it should catch,
> as in `@safe(ValueError)`, and lets anything else propagate.
> Show that a `TypeError` raised inside the wrapped function now propagates,
> where the original `@safe` returned it as an `Err`.

<details>
<summary>Where to look</summary>

[Turning Exceptions into Results](../../Chapters/42_Functional--Error_Handling.md#turning-exceptions-into-results)
shows `@safe` as a decorator that catches every `Exception`.
To take arguments, `safe()` becomes a function that receives the exception types and returns the decorator.
An `except` clause accepts a tuple of exception types,
so the wrapper changes in one place.
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
<summary>Done when</summary>

a `parse()` decorated with `@safe(ValueError)` returns `Ok(answer=42)` for `"42"`,
a `TypeError` raised inside it propagates out of the call instead of coming back as an `Err`,
and `reveal_type(parse)` under `uv run ty check` shows `(text: str) -> Result[int, Exception]`.

<details>
<summary>Solution</summary>

If you pass the exception type to the chapter's one-layer `safe()`,
`@safe(ValueError)` wraps `ValueError` as if it were the function.
Python then calls that wrapper with `parse()` as its argument,
so `parse` names an `Ok` holding a `ValueError`.
Calling `parse("42")` then raises a `TypeError`: `'Ok' object is not callable`.
`ty` reports `call-non-callable` at the same call.
The solution adds an outer layer.
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

**Type the returned decorator.**
`safe()` returns a decorator generic over the function it decorates.
The `SafeDecorator` protocol gives that decorator a generic `__call__`,
so `parse` keeps the signature `(text: str) -> Result[int, Exception]`.

A nested `Callable` annotation types `parse` as precisely as the protocol does.
If `safe()` declares `[**P, A]` and returns `Callable[[Callable[P, A]], Callable[P, Result[A, Exception]]]`,
`ty` reveals `parse` as `(text: str) -> Ok[int] | Err[Exception]`.
Under that annotation,
one `safe(ValueError)` decorator also stays generic across two different functions.
The protocol is a readability choice.
It gives the decorator's shape a name,
so `safe()`'s return annotation reads `SafeDecorator` and the revealed signature keeps the `Result` alias.

**Accept the types to catch.**
Python evaluates `safe(ValueError)` before it decorates anything,
so `safe()` must return the decorator.

**Catch only the named types.**
Because the `except catch` clause accepts a tuple of exception types,
`wrapper()` changes by one word.

**Let everything else propagate.**
`parse("oops")` raises a `TypeError`,
which `@safe(ValueError)` lets propagate out of `wrapper()` to the `expect()` call outside `parse()`.

A caller of `parse("oops")` receives the `TypeError` like any other exception.
The chapter's `@safe` returns the `TypeError` as `Err(TypeError(...))`,
the same shape a bad-input failure takes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Attaching Context to an Exception](../../Chapters/42_Functional--Error_Handling.md#attaching-context-to-an-exception)
shows `add_note()` and the `__notes__` list it fills.
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
<summary>Done when</summary>

a chain whose first load fails prints a note naming the first setting and its text,
a chain whose second load fails prints the second setting's note,
and no run prints a traceback.
You can answer the question by pointing to the path a successful call takes through `load_setting()`.

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

**Note only the failing path.**
A successful `load_setting()` returns its `Ok` from inside the `try` block and never reaches `add_note()`,
which sits in the `except` clause.
An `Ok` holds an answer, while notes attach to exceptions.
A note therefore travels with a failure,
the one result that has something to explain.

**Report without a traceback.**
The `Err` holds the exception,
and the exception holds the note as ordinary data,
so `report()` prints the note from that data after `load_setting()` has returned.
The exception keeps its `__traceback__`,
but `load_setting()` returns the exception inside an `Err`,
so it never propagates to the top-level handler that prints a traceback.

**Sequence the two loads.**
The lambdas ignore their parameter,
since the second load works from its own name and text.
`bind()` exists to pass one step's answer to the next step,
so it reads worst when the next step ignores that answer.
The `returns` library's [do-notation](../../Chapters/42_Functional--Error_Handling.md#the-returns-library)
reads better.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Reaching the Answer](../../Chapters/42_Functional--Error_Handling.md#reaching-the-answer)
compares `None` with `Result`,
and [Composing by Hand](../../Chapters/42_Functional--Error_Handling.md#composing-by-hand)
has the chain to adapt.
Return `None` where each function returned an `Err`,
and replace each `isinstance` test with `is None`.
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
<summary>Done when</summary>

for inputs `0` through `4` your run prints `0 0` and `4 4`,
with the same `None` for `1`, `2`, and `3`,
and you can name what those three lines lose compared with `composing.py`'s output for the same inputs.

<details>
<summary>Solution</summary>

If you test with `if not a:` and `if not b:` instead of `is None`,
input `0` prints `0 None`.
`func_a(0)` succeeds with `0`, which is falsy,
so `composed()` treats a success as a failure.
The type checker accepts that version.
The solution compares with `is None`,
which separates a missing value from a zero.

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

The three failures become one result.
Inputs `1`, `2`, and `3` fail in three different functions for three different reasons.
Compare the `Result` version, where the same three inputs report `func_a(1)`,
`func_b(2)`, and `func_c(3): division by zero`.

**Stop at the first failure.**
The structure of `composed()` barely changes.
`if a is None` replaces `if isinstance(a, Err)`, and the early returns stay.
What changes is the value each early return gives the caller.
`None` is one value and holds no reason,
so the caller receives the same `None` from every failing step.

The chapter [weighs `None` against `Result`](../../Chapters/42_Functional--Error_Handling.md#reaching-the-answer).
Use `| None` when the caller needs to know whether a step succeeded.
Use a `Result` when the caller may need to act on which failure occurred,
or when a person reading a bug report needs to know which of three steps went wrong.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
