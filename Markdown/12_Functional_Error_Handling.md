# Functional Error Handling

The [Data Classes as Types](10_Data_Classes_as_Types.md) chapter made a value carry a guarantee.
This chapter does the same for errors.
Instead of raising an exception,
a function returns its error as an ordinary value,
and the type system tracks it.

Exceptions are Python's default error mechanism, and they have real costs.
An exception unwinds the stack, so it discards any work done so far.
It does not appear in the function's return type, so the caller cannot see,
from the signature, that the call might fail.
And it is easy to forget to handle.
This material comes from my PyCon 2024 talk,
[Functional Error Handling](https://github.com/BruceEckel/functional_error_handling).

## Exceptions Throw Everything Away

Here a function raises an exception partway through a comprehension.
The successful results computed before the failure are lost with the rest:

```python
# exceptions_lose_data.py
# An exception unwinds the whole computation. Partial results are
# thrown away: func_a(0) succeeded, but its result is gone.

def func_a(i: int) -> int:
    if i == 1:
        raise ValueError(f"func_a({i})")
    return i

try:
    results = [func_a(i) for i in range(3)]
    print(results)
except ValueError as e:
    print(f"Lost everything: {e}")
```

The output is:

    Lost everything: func_a(1)

`func_a(0)` produced a value, but the exception threw away the whole list.
The only way to keep the good results is to wrap each call in its own `try`,
which is the kind of scattering the [Data Classes as Types](10_Data_Classes_as_Types.md) chapter warned against.

## Return the Error as a Value

The alternative is to return the error.
The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type*: a value that is one thing or another.
Nothing is thrown away, because the error is just another return value:

```python
# sum_type.py
# Return the error as a value instead of raising. The return type
# becomes a union, a "sum type". Nothing is lost, but success and
# failure are not clearly distinguished: both are just values you
# have to tell apart by type.

def func_a(i: int) -> int | str:
    if i == 1:
        return f"func_a({i})"  # The error, returned as a value
    return i

outputs = [func_a(i) for i in range(3)]
print(outputs)

for r in outputs:
    match r:
        case int(answer):
            print(f"answer = {answer}")
        case str(error):
            print(f"error = {error!r}")
```

The output is:

    [0, 'func_a(1)', 2]
    answer = 0
    error = 'func_a(1)'
    answer = 2

This keeps every result,
and `match` (covered in the [Pattern Matching](11_Pattern_Matching.md) chapter) tells the two cases apart.
But the distinction rides on the types `int` and `str`, which is fragile.
If a successful answer were also a string, the two cases would collide.
We need something that says "success" or "failure" no matter what types they carry.

## A Result Type

Make the success and failure explicit.
`Success` wraps an answer, `Failure` wraps an error,
and `Result` is the union of the two.
Both are frozen data classes,
parameterized over the answer type and the error type:

```python
# result.py
# A Result is either a Success holding an answer, or a Failure
# holding an error. Both are frozen, like the types in the Data
# Classes as Types chapter. bind chains steps: it feeds a Success
# into the next function, and passes a Failure straight through
# unchanged.

from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Success[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

@dataclass(frozen=True)
class Failure[E]:
    error: E

    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Failure[E]:
        return self  # Pass the failure forward unchanged

type Result[A, E] = Success[A] | Failure[E]
```

Ignore `bind` for the moment.
The two data classes and the `Result` alias are enough to report errors.
A function that might fail returns a `Result`.
Now the signature tells the whole story:

```python
# returning_result.py
# A function reports failure by returning Failure, success by
# returning Success. The return type now says exactly that:
# Result[int, str].
from result import Failure, Result, Success

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)

if __name__ == "__main__":
    for i in range(3):
        print(i, func_a(i))
```

The output is:

    0 Success(answer=0)
    1 Failure(error='func_a(1)')
    2 Success(answer=2)

`Result[int, str]` says this function returns an `int` on success or a `str` on failure.
The caller cannot ignore that,
because to get the answer it has to open the `Result`.
This is the same idea as the [Static Typing](07_Static_Typing.md) chapter:
put the meaning in the type.

## Composing by Hand

Real programs chain steps.
With a `Result`, each step can fail,
so each call has to be checked before the next one runs.
An exception from existing code can be caught and turned into a `Failure`,
so the failure becomes data rather than control flow:

```python
# composing.py
# Composing functions that return Results, by hand. Each step checks
# for a Failure and returns early. An exception can be turned into a
# Failure value instead of being raised.
from result import Failure, Result, Success
from returning_result import func_a

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Failure(f"func_b({i})")
    return Success(i)

def func_c(i: int) -> Result[int, str]:
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        # The exception becomes a value:
        return Failure(f"func_c({i}): {e}")
    return Success(i)

def composed(i: int) -> Result[int, str]:
    a = func_a(i)
    if isinstance(a, Failure):
        return a
    b = func_b(a.unwrap())
    if isinstance(b, Failure):
        return b
    return func_c(b.unwrap())

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
```

The output is:

    0 Success(answer=0)
    1 Failure(error='func_a(1)')
    2 Failure(error='func_b(2)')
    3 Failure(error='func_c(3): division by zero')
    4 Success(answer=4)

This works, and it keeps errors as values, but the shape is repetitive.
Every step is the same dance: call, check for `Failure`, return early, unwrap,
go on.

## Composing With bind

`bind` captures that dance once.
Look again at the method on `Result`.
On a `Success`, `bind` feeds the answer to the next function.
On a `Failure`, `bind` ignores the function and returns the failure unchanged.
So a `Failure` anywhere in a chain skips the rest of the steps and falls through to the end:

```python
# composing_with_bind.py
# Bind removes the boilerplate. Chain the steps; a Failure anywhere
# in the chain short-circuits the rest and is passed through to the
# end.
from composing import func_b, func_c
from result import Result
from returning_result import func_a

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c)

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
```

The output is identical to the hand-written version:

    0 Success(answer=0)
    1 Failure(error='func_a(1)')
    2 Failure(error='func_b(2)')
    3 Failure(error='func_c(3): division by zero')
    4 Success(answer=4)

The body is now one line that reads in order: `func_a`, then `func_b`,
then `func_c`.
The error checking has not gone away.
It moved into `bind`, where it is written once.
A type that carries a value plus this chaining operation is what functional programmers call a *monad*.
You do not need the word to use it.

## Combining Multiple Results

`bind` threads one value through a chain.
When you have several independent inputs,
nest the binds so each answer stays in scope for the next step.
The first `Failure` still short-circuits the whole thing:

```python
# combining.py
# Combining several Results that come from different inputs. Nested
# binds carry each answer inward; a Failure anywhere short-circuits
# to the end.
from composing import func_b, func_c
from result import Result, Success
from returning_result import func_a

def add(a: int, b: int, c: int) -> str:
    return f"add({a} + {b} + {c}): {a + b + c}"

def combined(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: func_c(i + j).bind(
                lambda c: Success(add(a, b, c)))))

if __name__ == "__main__":
    for args in [(1, 5), (7, 2), (2, 1), (7, 5)]:
        print(args, combined(*args))
```

The output is:

    (1, 5) Failure(error='func_a(1)')
    (7, 2) Failure(error='func_b(2)')
    (2, 1) Failure(error='func_c(3): division by zero')
    (7, 5) Success(answer='add(7 + 5 + 12): 24')

Only the last input passes all three steps, so only it reaches `add`.

## Turning Exceptions into Results

In `composing.py`, `func_c` wrapped a risky call in `try`/`except` and returned a `Failure` by hand.
A decorator captures that pattern once.
`@safe` takes a function that raises an exception and gives back one that returns a `Result`,
with the exception as the `Failure` value:

```python
# safe.py
# @safe turns a function that raises into one that returns a Result.
# The exception becomes the Failure value, so a caller handles it like
# any other Result.
from collections.abc import Callable
from functools import wraps
from result import Failure, Result, Success

def safe[A](
    func: Callable[..., A],
) -> Callable[..., Result[A, Exception]]:
    @wraps(func)
    def wrapper(
        *args: object, **kwargs: object
    ) -> Result[A, Exception]:
        try:
            return Success(func(*args, **kwargs))
        except Exception as e:
            return Failure(e)
    return wrapper

@safe
def parse(text: str) -> int:
    return int(text)

if __name__ == "__main__":
    for text in ("42", "oops"):
        match parse(text):
            case Success(answer):
                print(f"{text}: parsed {answer}")
            case Failure(error):
                print(f"{text}: {type(error).__name__}")
```

The output is:

    42: parsed 42
    oops: ValueError

`parse` still reads like a normal function that returns an `int`,
but `@safe` has changed its type to `Result[int, Exception]`.
The caller cannot ignore the failure,
because it has to open the `Result` to reach the number.

## Matching on the Error

Because the error is a value, and is often an exception,
you can pattern-match the `Result` and the exception type together.
Each kind of failure gets its own branch:

```python
# matching_errors.py
# Because the error is a value, often an exception, you can match the
# Result and the exception type together, and handle each kind.
from result import Failure, Result, Success
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

@safe
def reciprocal(n: int) -> float:
    return 1 / n

def describe(text: str) -> str:
    result: Result[float, Exception] = parse(text).bind(reciprocal)
    match result:
        case Success(answer):
            return f"{text}: {answer}"
        case Failure(ValueError()):
            return f"{text}: not a number"
        case Failure(ZeroDivisionError()):
            return f"{text}: cannot divide by zero"
        case Failure(error):
            return f"{text}: {type(error).__name__}"

if __name__ == "__main__":
    for text in ("4", "0", "oops"):
        print(describe(text))
```

The output is:

    4: 0.25
    0: cannot divide by zero
    oops: not a number

`parse` and `reciprocal` are both wrapped with `@safe`, so `bind` chains them.
A `ValueError` from a bad number and a `ZeroDivisionError` from dividing by zero arrive as ordinary `Failure` values,
and the `match` tells them apart.

## The returns Library

You do not have to build `Result` yourself.
The [returns](https://github.com/dry-python/returns) library provides a `Result` type with `Success` and `Failure`,
the same `@safe` decorator we just built,
and do-notation that makes combining multiple results read more directly than nested binds.
Building the type here, in a few lines, shows that there is no magic in it.

This style does not replace exceptions everywhere.
Exceptions are still right for truly exceptional conditions,
the ones no caller can reasonably handle,
such as running out of memory or a programming bug.
Use a `Result` for the failures that are part of a function's normal job:
bad input, a missing file, a value out of range.
Those are not exceptional.
They are expected, and the type should say so.

## Testing the Behavior

Because failures are values, you can assert on them directly,
without `pytest.raises`.
The tests below check that `bind` chains a success and short-circuits a failure,
that the hand-written and `bind` versions agree,
and that combining returns the right value.
See the [Testing](09_Testing.md) chapter for pytest in general.

```python
# test_result.py
from combining import combined
from composing import composed as composed_manual
from composing_with_bind import composed as composed_bind
from result import Failure, Success

def test_success_unwrap() -> None:
    assert Success(5).unwrap() == 5

def test_bind_chains_a_success() -> None:
    assert Success(1).bind(lambda x: Success(x + 1)) == Success(2)

def test_bind_short_circuits_a_failure() -> None:
    failure: Failure[str] = Failure("boom")
    assert failure.bind(lambda x: Success(x + 1)) is failure

def test_manual_and_bind_agree() -> None:
    for i in range(5):
        assert composed_manual(i) == composed_bind(i)

def test_combined() -> None:
    assert combined(7, 5) == Success("add(7 + 5 + 12): 24")
    assert combined(1, 5) == Failure("func_a(1)")
    assert combined(2, 1) == Failure("func_c(3): division by zero")
```

`@safe` deserves its own check: a good input becomes a `Success`,
and a raised exception becomes a `Failure` holding that exception.

```python
# test_safe.py
from result import Failure, Success
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

def test_safe_wraps_a_success() -> None:
    assert parse("42") == Success(42)

def test_safe_captures_the_exception() -> None:
    match parse("oops"):
        case Failure(error):
            assert isinstance(error, ValueError)
        case _:
            raise AssertionError("expected a Failure")
```

## Exercises

1.  Add a `func_e` that returns a `Result[int, str]`,
    and extend the `bind` chain in `composing_with_bind.py` to include it.
    Confirm a `Failure` from `func_e` still short-circuits.
2.  Give `Failure` a `map_error` method that transforms the error it holds,
    leaving a `Success` untouched.
    Use it to add a prefix to every error.
3.  Rewrite `combined` so it collects all the failures instead of stopping at the first one,
    returning `Result[str, list[str]]`.
    Write the tests first.
