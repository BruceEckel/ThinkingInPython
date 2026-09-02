# Error Handling

[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
made a value carry a guarantee.
This chapter does the same for errors.
Instead of raising an exception,
a function returns its error as an ordinary value,
and the type system tracks it.

Exceptions are Python's default error mechanism, and they have costs.
An exception unwinds the stack, so it discards any work done so far.
It does not appear in the function's return type,
so the caller cannot see from the signature that the call might fail.
And forgetting to handle one is easy.

Returning the failure as a value reverses those costs.
Failure appears in the return type,
so the type checker forces a caller to deal with the failure before reading the answer,
and a reviewer sees it without reading the body.
Control flow stays local,
with no exception leaping past intermediate frames to a distant handler.
You do pay by handling the failure at each step,
but that is the same discipline that stops an unhandled error from escaping unnoticed.

This material comes from my PyCon 2024 talk,
[Functional Error Handling](https://github.com/BruceEckel/functional_error_handling).

## Exceptions Discard Partial Calculations

If a function raises an exception partway through a comprehension,
you lose all partial calculations:

```python
# exceptions_lose_data.py

def func_a(i: int) -> int:
    print(f"Calculating func_a({i})")
    if i == 3:
        raise ValueError(f"func_a({i})")
    return i

try:
    results = [func_a(i) for i in range(5)]
    print(results)
except ValueError as e:
    print(f"Lost everything: {e}")
#: Calculating func_a(0)
#: Calculating func_a(1)
#: Calculating func_a(2)
#: Calculating func_a(3)
#: Lost everything: func_a(3)
```

Function calls 0-2 produce correct values,
but the exception throws away the whole list.
To keep the good results you must wrap each call in its own `try`,
the kind of scattering [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-value-to-check-everywhere)
flags as a problem.

## Return the Error as a Value

The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type* (a *disjoint* union):
a value that is one thing or another.
Python's union carries no tag,
so only the runtime type of the value says which side you received.
The error is just another return value, so every result survives:

```python
# sum_type.py

def func_a(i: int) -> int | str:
    if i == 3:
        # The error, returned as a value
        return f"func_a({i})"
    return i

outputs = [func_a(i) for i in range(5)]
print(outputs)
#: [0, 1, 2, 'func_a(3)', 4]

for r in outputs:
    match r:
        case int(answer):
            print(f"answer = {answer}")
        case str(error):
            print(f"error = {error!r}")
#: answer = 0
#: answer = 1
#: answer = 2
#: error = 'func_a(3)'
#: answer = 4
```

`match` (see [Pattern Matching](13_Techniques--Pattern_Matching.md#matching-values))
tells the two cases apart.
But the distinction rests on the types `int` and `str`,
and that dependence is fragile.
If a successful answer were also a string, the two cases would collide.
You need something that says "success" or "failure" no matter what types they carry.

## A Result Type

Make success and failure explicit by defining them as types.
`Ok` wraps an answer, `Err` wraps an error,
and `Result` is the union of the two.
The class is now the tag that tells the two cases apart,
so the union stays unambiguous whatever the two sides carry.
Other languages call this a *tagged* or *discriminated* union.
`Ok` and `Err` are both frozen data classes,
`Ok` parameterized over the answer type and `Err` over the error type.
`@final` states that neither can have subclasses.
Narrowing a `Result` to exactly one of the two comes from the union itself.
`A`, `B`, and `E` are type parameters
(introduced in [Static Types](08_Foundations--Static_Types.md#generic-functions-and-classes)):
placeholders that take concrete types when you use the class.
Here they have no bounds or constraints, so any type can fill them.
`Result` is useful beyond this chapter,
so it lives in `utils/` and any chapter can import it:

```python
# utils/result.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import final

@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

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
        return self  # Pass the failure forward unchanged

type Result[A, E] = Ok[A] | Err[E]
```

Ignore `bind()` for the moment.
The two data classes and the `Result` alias are enough to report errors.
A function that might fail returns a `Result`.
The signature tells the story:

```python
# returning_result.py
from result import Err, Ok, Result

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Err(f"func_a({i})")
    return Ok(i)

if __name__ == "__main__":
    for i in range(5):
        print(i, func_a(i))
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Ok(answer=2)
#: 3 Ok(answer=3)
#: 4 Ok(answer=4)
```

A function reports failure by returning an `Err` object,
success by returning an `Ok` object.

`Result[int, str]` says this function returns an `int` on success or a `str` on failure.
To get the answer, the caller must unpack the `Result`.
`unwrap()` makes that literal: only `Ok` defines it,
so `func_a(i).unwrap()` fails the type checker,
and so does using the `Result` as if it were a number.
The one route to the answer is narrowing to one of the two classes.
The asymmetry is visible at runtime as well as to the type checker:

```python
# must_unwrap.py
from result import Err, Ok
from returning_result import func_a

print(hasattr(Ok(1), "unwrap"), hasattr(Err("x"), "unwrap"))
#: True False
try:
    func_a(1).unwrap()  # type: ignore
except AttributeError as e:
    print(e)
#: 'Err' object has no attribute 'unwrap'
```

The `# type: ignore` is the point of the listing rather than an apology for it.
Without that comment `ty` refuses the line,
reporting that `Err[str]` in the union has no `unwrap`,
and a reader who writes this in their own code meets that report instead of the traceback.

This is the same idea as in [Static Types](08_Foundations--Static_Types.md#type-hints):
put the meaning in the type.
Python's humbler form of the same idea is `int | None`.
Both force the caller to unpack, but `None` says only "no answer,"
while an `Err` carries the reason for the failure.
Use `| None` when absence is the whole story, a lookup that found nothing.
Use `Result` when the caller may need to act on the reason,
or when several different failures must stay distinguishable,
as [Matching on the Error](#matching-on-the-error) shows below.

A function like this is a *Total Function*:
its return type accounts for every outcome it can produce, success or failure.
Raise an exception instead,
and the signature hides that outcome from a caller reading the return type.
Totality is a discipline the function's author keeps,
since Python lets a `Result`-returning function raise as well and the type checker has no way to tell.
The caller has a matching gap:
a statement that calls the function and discards the `Result` passes the checker.
The type checker stops you from misreading a `Result`;
ignoring one is still up to you.

## Composing by Hand

Real programs chain steps.
With a `Result`, each step can fail,
so you must check each call before the next one runs.
You can catch an exception from existing code and turn it into an `Err`,
so the failure becomes data rather than control flow:

```python
# composing.py
from result import Err, Ok, Result
from returning_result import func_a

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Err(f"func_b({i})")
    return Ok(i)

def func_c(i: int) -> Result[int, str]:
    try:
        # A probe: raises an exception when i == 3
        1 / (i - 3)
    except ZeroDivisionError as e:
        # The exception becomes a value:
        return Err(f"func_c({i}): {e}")
    return Ok(i)

def composed(i: int) -> Result[int, str]:
    a = func_a(i)
    if isinstance(a, Err):
        return a
    b = func_b(a.unwrap())
    if isinstance(b, Err):
        return b
    return func_c(b.unwrap())

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Err(error='func_b(2)')
#: 3 Err(error='func_c(3): division by zero')
#: 4 Ok(answer=4)
```

Each step returns early when it encounters an `Err`.
The check names `Err`, one of the two concrete classes,
because `Result` is a `type` alias rather than a class:
`isinstance(a, Result)` fails the type checker and, if run anyway,
raises a `TypeError`.

This works, and it keeps errors as values, but every step is the same dance:
call, check for `Err`, return early, unwrap, go on.

## Composing With bind

`bind()` captures the dance.
Look again at the two `bind()` methods in `result.py`.
On an `Ok`, `bind()` feeds the answer to the next function.
On an `Err`, it ignores the function and returns the failure unchanged.
The two signatures differ because `Err` holds no answer to feed the next step.
With nothing to name the argument type, its `bind()` accepts any parameter list,
and its return type says an `Err` comes back out.
An `Err` anywhere in a chain skips the rest of the steps and falls through to the end:

```python
# composing_with_bind.py
from composing import func_b, func_c
from result import Result
from returning_result import func_a

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c)

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Err(error='func_b(2)')
#: 3 Err(error='func_c(3): division by zero')
#: 4 Ok(answer=4)
```

The body is now one line that reads in order: `func_a()`, then `func_b()`,
then `func_c()`.
`bind()` removes the boilerplate by chaining the steps.
The error checking moved into `bind()`, where it appears once.

Functional programmers have a name for a type that carries a value plus this chaining operation:
a *monad*.
You do not need to know that word to use functional error handling.
The word marks a reusable shape: `Maybe` chains a value that might be absent,
`Result` chains one that might have failed,
and an async container chains one that has not arrived yet,
all with the same `bind()`.

One mistake to expect when you start chaining:
`bind()` requires each step to return a `Result`.
If you feed it a plain function, say `.bind(str)`,
the type checker rejects that call immediately, because `str` returns a `str`,
and `bind()` expects a `Result`.
To chain a plain function, wrap its return value: `.bind(lambda x: Ok(str(x)))`.
Libraries like `returns` name that pattern `map()`,
a sibling of `bind()` for steps that cannot fail,
and exercise 2's `map_error()` is the same idea aimed at the error side.

Because failures are values, you can assert on them directly,
with no `pytest.raises()`.
The tests check that `unwrap()` returns the answer,
and that `bind()` chains a success and short-circuits a failure.
The last assertion uses `is` rather than `==`,
proving the same `Err` object comes back and the lambda does not run:

```python
# test_result.py
from result import Err, Ok

def test_success_unwrap() -> None:
    assert Ok(5).unwrap() == 5

def test_bind_chains_a_success() -> None:
    assert Ok(1).bind(lambda x: Ok(x + 1)) == Ok(2)

def test_bind_short_circuits_a_failure() -> None:
    failure: Err[str] = Err("boom")
    assert failure.bind(lambda x: Ok(x + 1)) is failure
```

The tests confirm that the hand-written and `bind()` versions agree on every input:

```python
# test_composing.py
from composing import composed as composed_manual
from composing_with_bind import composed as composed_bind

def test_manual_and_bind_agree() -> None:
    for i in range(5):
        assert composed_manual(i) == composed_bind(i)
```

## Combining Multiple Results

`bind()` threads one value through a chain.
When you have several independent inputs,
nest the binds so each answer stays in scope for the next step.
Two inputs show the shape:

```python
# combining_two.py
from composing import func_b
from result import Ok, Result
from returning_result import func_a

def pair(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: Ok(f"{a} and {b}")))

if __name__ == "__main__":
    for args in [(7, 5), (1, 5), (7, 2)]:
        print(args, pair(*args))
#: (7, 5) Ok(answer='7 and 5')
#: (1, 5) Err(error='func_a(1)')
#: (7, 2) Err(error='func_b(2)')
```

Each lambda's parameter is the previous step's answer,
and the answers stay reachable because the nesting keeps them in scope:
`a` is still visible inside the inner lambda where `b` arrives.
A flat sequence of `bind()` calls could not give you that,
because each step would see only the value handed to it.

A third input adds a third level:

```python
# combining.py
from composing import func_b, func_c
from result import Ok, Result
from returning_result import func_a

def add(a: int, b: int, c: int) -> str:
    return f"add({a} + {b} + {c}): {a + b + c}"

def combined(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: func_c(i + j).bind(
                lambda c: Ok(add(a, b, c)))))

if __name__ == "__main__":
    for args in [(1, 5), (7, 2), (2, 1), (7, 5)]:
        print(args, combined(*args))
#: (1, 5) Err(error='func_a(1)')
#: (7, 2) Err(error='func_b(2)')
#: (2, 1) Err(error='func_c(3): division by zero')
#: (7, 5) Ok(answer='add(7 + 5 + 12): 24')
```

Nested binds carry each answer inward.
An `Err` anywhere short-circuits to the end.
Only the last input passes all three steps,
so it's the only one that reaches `add()`.
Three inputs cost three levels of nesting,
and the shape gets worse with each one you add.
[The returns Library](#the-returns-library)
at the end of this chapter has do-notation,
which writes the same combination flat.

The tests confirm that `combined()` returns the correct value,
or the first failure in the chain:

```python
# test_combining.py
import pytest
from combining import combined
from result import Err, Ok, Result

@pytest.mark.parametrize("a, b, expected", [
    (7, 5, Ok("add(7 + 5 + 12): 24")),
    (1, 5, Err("func_a(1)")),
    (7, 2, Err("func_b(2)")),
    (2, 1, Err("func_c(3): division by zero")),
])
def test_combined(
    a: int, b: int, expected: Result[str, str]
) -> None:
    assert combined(a, b) == expected
```

## Turning Exceptions into Results

In `composing.py`, `func_c()` wraps a risky call in `try`/`except` and returns an `Err` by hand.
A decorator can capture that pattern.
`@safe` takes a function that raises an exception and gives back one that returns a `Result`,
with the exception as the `Err` value.
Like `result.py`, it lives in `utils/` and any chapter can import it:

```python
# utils/safe.py
from collections.abc import Callable
from functools import wraps
from result import Err, Ok, Result

def safe[**P, A](
    func: Callable[P, A],
) -> Callable[P, Result[A, Exception]]:
    @wraps(func)
    def wrapper(
        *args: P.args, **kwargs: P.kwargs
    ) -> Result[A, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            return Err(e)
    return wrapper
```

Decorating a function that raises an exception is all it takes:

```python
# safe_demo.py
from result import Err, Ok
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

if __name__ == "__main__":
    for text in ("42", "oops"):
        match parse(text):
            case Ok(answer):
                print(f"{text}: parsed {answer}")
            case Err(error):
                print(f"{text}: {type(error).__name__}")
#: 42: parsed 42
#: oops: ValueError
```

`parse()` still reads like a normal function that returns an `int`,
but `@safe` has changed its return type to `Result[int, Exception]`.
The caller cannot ignore the failure,
because it must unpack the `Result` to reach the number.
The `**P` parameter carries the wrapped function's whole parameter list through,
the technique from [Decorators](14_Techniques--Decorators.md#maintaining-the-wrapped-interface),
so `parse("42")` type-checks and `parse(42)` does not:
`@safe` changes only the return type, never what the function accepts.

That chapter explains how to write decorators like `@safe`,
including `functools.wraps`.

`@safe` catches `Exception`,
which is every failure the wrapped function can produce,
including the ones that are defects rather than expected outcomes.
If you misspell a name inside the wrapped function,
the resulting `NameError` arrives as an ordinary `Err`,
indistinguishable from bad input.
The version here is deliberately small.
A production one takes the exception types to catch as an argument and lets the rest propagate.
That keeps the distinction the chapter ends on:
a failure the caller can handle versus a bug the caller cannot.

The tests for `@safe` check that a good input becomes an `Ok`,
and that a raised exception becomes an `Err` holding that exception:

```python
# test_safe.py
from result import Err, Ok
from safe_demo import parse

def test_safe_wraps_a_success() -> None:
    assert parse("42") == Ok(42)

def test_safe_captures_the_exception() -> None:
    match parse("oops"):
        case Err(error):
            assert isinstance(error, ValueError)
        case _:
            raise AssertionError("expected an Err")
```

## Matching on the Error

Because the error is a value, and is often an exception,
you can pattern-match the `Result` and the exception type together.
Each kind of failure gets its own branch:

```python
# matching_errors.py
from result import Err, Ok, Result
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

@safe
def reciprocal(n: int) -> float:
    return 1 / n

def describe(text: str) -> str:
    result: Result[float, Exception] = parse(text).bind(
        reciprocal)
    match result:
        case Ok(answer):
            return f"{text}: {answer}"
        case Err(ValueError()):
            return f"{text}: Not a number"
        case Err(ZeroDivisionError()):
            return f"{text}: Cannot divide by zero"
        case Err(error):
            return f"{text}: {type(error).__name__}"

if __name__ == "__main__":
    for text in ("4", "0", "OOPS"):
        print(describe(text))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

`@safe` wraps both `parse()` and `reciprocal()`, so `bind()` chains them.
A `ValueError` from a bad number and a `ZeroDivisionError` from dividing by zero arrive as ordinary `Err` values,
and the `match` tells them apart.

## Attaching Context to an Exception {#attaching-context-to-an-exception}

An exception knows what went wrong but not where.
`invalid literal for int() with base 10: 'no'` is accurate and unhelpful:
which setting, which field, which row of the file?
The frame that has that answer is rarely the frame that raised the exception,
and by the time the exception reaches a handler high enough to report it,
the local names that would explain it have vanished.

Most code catches the exception and raises a new one carrying a better message,
and that trade costs you the original type and gives every caller a wrapper to unwrap.
`BaseException.add_note()` (Python 3.11 and later) avoids the trade.
It appends a line to the exception you already have,
and the traceback prints it:

```python
# add_note.py
import traceback

def parse_seconds(text: str) -> int:
    try:
        return int(text)
    except ValueError as e:
        e.add_note(f"timeout was set to {text!r}")
        e.add_note("expected a whole number of seconds")
        raise

try:
    parse_seconds("no")
except ValueError as e:
    print("".join(traceback.format_exception_only(e)),
          end="")
#: ValueError: invalid literal for int() with base 10: 'no'
#: timeout was set to 'no'
#: expected a whole number of seconds
```

The bare `raise` re-raises the same object,
so the type stays `ValueError` and the original traceback survives undisturbed.
Notes accumulate: each frame that knows something the raiser did not can add its own line as the stack unwinds.
They live in a list called `__notes__`,
which the first `add_note()` call creates.
The type checker treats `__notes__` as always present,
because typeshed declares it on `BaseException` for every exception,
so reading it before any `add_note()` call type-checks and then raises an `AttributeError` at runtime.
The listing prints with `traceback.format_exception_only()`,
which renders the message and the notes and leaves out the file paths a full traceback would carry.

Context matters more here than in ordinary exception code,
because a `Result` keeps the exception as a value rather than propagating it.
An `Err` sitting in a list has no traceback to explain it.
The exception must carry whatever context it needs:

```python
# noted_result.py
from result import Err, Ok, Result

def parse_field(name: str,
                text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"field {name!r} received {text!r}")
        return Err(e)

for field, value in (("age", "42"), ("size", "oops")):
    match parse_field(field, value):
        case Ok(answer):
            print(f"{field} = {answer}")
        case Err(error):
            print(f"{field}: {type(error).__name__}")
            for note in error.__notes__:
                print(f"  {note}")
#: age = 42
#: size: ValueError
#:   field 'size' received 'oops'
```

The note attaches before the exception becomes a value,
in the one frame that knows both the failure and the field name.
Everything downstream can report the failure without asking what the code was reading.
This is the chapter's opening argument, applied one level down:
`Err` says the call failed, the exception says what went wrong,
and a note says which piece of work produced it.

The `Err` branch reads `error.__notes__`,
and that read type-checks because the `match` narrowed the `Result` to `Err`.
The narrowing works because `Result` is a union of exactly two classes,
and it works the same way with `isinstance()`.

## The returns Library

You need not build `Result` yourself.
The [returns](https://github.com/dry-python/returns)
library provides a `Result` type whose two cases it calls `Success` and `Failure`,
the same `@safe` decorator you built earlier in this chapter,
and do-notation that makes combining multiple results read more directly than nested binds.

## Which Failures Get a Result

A `Result` does not replace every exception.
Exceptions are still appropriate for truly exceptional conditions,
the ones no caller can reasonably handle,
such as running out of memory or a programming bug.
Some languages call these errors *panics* and separate them from regular exceptions.

Use a `Result` for the failures that are part of a function's normal job:
bad input, a missing file, a value out of range.
Those are not exceptional.
They are routine, and the type should say so.

You can now write a function whose signature admits it can fail,
and chain three of them without a single `try` in the calling code.
The chain either delivers an answer or hands back the first failure,
and the type checker keeps a caller from confusing the two.
[Confidence](43_Functional--Confidence.md)
examines what this discipline lets you claim,
and [Effect Management](44_Effects--Effect_Management.md#converting-effectful-to-pure)
reuses this `Result` machinery to convert Effects.

## Exercises

1.  Add a `func_e()` that returns a `Result[int, str]`,
    and extend the `bind()` chain in `composing_with_bind.py` to include it.
    Put it in the middle of the chain rather than at the end,
    so an `Err` from it has a later step to skip,
    and confirm that the step never runs.
2.  Give `Err` a `map_error()` method that transforms the error it holds,
    leaving an `Ok` untouched
    (for chains to keep working, `Ok` needs its own `map_error()` that returns `self`).
    Use it to add a prefix to every error.
3.  Rewrite `combined` so it collects all the failures instead of stopping at the first one,
    returning `Result[str, list[str]]`.
    Write the tests first.
4.  Change `@safe` so it takes the exception types it should catch,
    as in `@safe(ValueError)`, and lets anything else propagate.
    Show that a `TypeError` raised inside the wrapped function now escapes instead of arriving as an `Err`.
5.  Write `load_setting(name, text)` that returns `Result[int, Exception]` and attaches a note naming the setting.
    Chain two of them with `bind()` and print the notes from whichever one failed.
    What happens to the note the successful call would have added?
6.  Rewrite `func_a()`, `func_b()`, and `func_c()` to return `int | None` instead of `Result[int, str]`,
    and adjust `composing.py` to match.
    What can the caller still tell about which of the three steps failed?
