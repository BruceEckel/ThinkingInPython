# Functional Error Handling

[Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values) made a value carry a guarantee.
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
An exception discards the whole computation,
so the successful results computed before the failure are lost:

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

Function calls 0-2 produced values, but the exception threw away the whole list.
The only way to keep the good results is to wrap each call in its own `try`,
which is the kind of scattering [Data Classes as Types](12_Data_Classes_as_Types.md#a-value-that-must-be-checked-everywhere) warns against.

## Return the Error as a Value

The alternative is to return the error.
The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type*: a value that is one thing or another.
Nothing is thrown away, because the error is just another return value:

```python
# sum_type.py

def func_a(i: int) -> int | str:
    if i == 3:
        return f"func_a({i})"  # The error, returned as a value
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

This keeps every result,
and `match` (covered in [Pattern Matching](13_Pattern_Matching.md#matching-values)) tells the two cases apart.
But the distinction rides on the types `int` and `str`, which is fragile.
If a successful answer were also a string, the two cases would collide.
We need something that says "success" or "failure" no matter what types they carry.

## A Result Type

Make success and failure explicit by defining them as types.
`Success` wraps an answer, `Failure` wraps an error,
and `Result` is the union of the two.
Both are frozen data classes,
parameterized over the answer type and the error type.
`A`, `B`, and `E` are type parameters:
placeholders that are filled in with concrete types when the class is used.
Here they have no constraints, which allows them to be used in any context:

```python
# result.py
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

Ignore `bind()` for the moment.
The two data classes and the `Result` alias are enough to report errors.
A function that might fail returns a `Result`.
The signature tells the story:

```python
# returning_result.py
from result import Failure, Result, Success

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)

if __name__ == "__main__":
    for i in range(5):
        print(i, func_a(i))
#: 0 Success(answer=0)
#: 1 Failure(error='func_a(1)')
#: 2 Success(answer=2)
#: 3 Success(answer=3)
#: 4 Success(answer=4)
```

A function reports failure by returning a `Failure` object,
success by returning a `Success` object.

`Result[int, str]` says this function returns an `int` on success or a `str` on failure.
The caller cannot pretend the function returns an ordinary value; to get the answer `Result` must be unpacked.
This is the same idea as in [Static Typing](08_Static_Typing.md#type-hints):
put the meaning in the type.

Because failures are values, you can assert on them directly, with no `pytest.raises()`. These check `unwrap()` and that `bind()` chains a success and short-circuits a failure:

```python
# test_result.py
from result import Failure, Success

def test_success_unwrap() -> None:
    assert Success(5).unwrap() == 5

def test_bind_chains_a_success() -> None:
    assert Success(1).bind(lambda x: Success(x + 1)) == Success(2)

def test_bind_short_circuits_a_failure() -> None:
    failure: Failure[str] = Failure("boom")
    assert failure.bind(lambda x: Success(x + 1)) is failure
```

## Composing by Hand

Real programs chain steps.
With a `Result`, each step can fail,
so each call must be checked before the next one runs.
An exception from existing code can be caught and turned into a `Failure`,
so the failure becomes data rather than control flow:

```python
# composing.py
# Composing functions that return Results, by hand.
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
#: 0 Success(answer=0)
#: 1 Failure(error='func_a(1)')
#: 2 Failure(error='func_b(2)')
#: 3 Failure(error='func_c(3): division by zero')
#: 4 Success(answer=4)
```

Each step returns early when it encounters a `Failure`.
This works, and it keeps errors as values,
but every step is the same dance: call, check for `Failure`, return early, unwrap,
go on.

## Composing With bind

`bind()` captures the dance.
Look again at the `bind()` method on `Result`.
On a `Success`, it feeds the answer to the next function.
On a `Failure`, it ignores the function and returns the failure unchanged.
So a `Failure` anywhere in a chain skips the rest of the steps and falls through to the end:

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
#: 0 Success(answer=0)
#: 1 Failure(error='func_a(1)')
#: 2 Failure(error='func_b(2)')
#: 3 Failure(error='func_c(3): division by zero')
#: 4 Success(answer=4)
```

The body is now one line that reads in order: `func_a()`, then `func_b()`,
then `func_c()`.
Bind removes the boilerplate by chaining the steps.
The error checking has not gone away;
it moved into `bind()`, where it is written once.
A `Failure` anywhere short-circuits the whole thing.

A type that carries a value plus this chaining operation is what functional programmers call a *monad*.
You do not need to know that word to use it.

Testing confirms the hand-written and `bind()` versions agree on every input:

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
nest the binds so each answer stays in scope for the next step:

```python
# combining.py
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
#: (1, 5) Failure(error='func_a(1)')
#: (7, 2) Failure(error='func_b(2)')
#: (2, 1) Failure(error='func_c(3): division by zero')
#: (7, 5) Success(answer='add(7 + 5 + 12): 24')
```

Nested binds carry each answer inward; a `Failure` anywhere short-circuits to the end.
Only the last input passes all three steps, so it's the only one that reaches `add()`.

Testing confirms combining returns the right value, or the first failure in the chain:

```python
# test_combining.py
from combining import combined
from result import Failure, Success

def test_combined() -> None:
    assert combined(7, 5) == Success("add(7 + 5 + 12): 24")
    assert combined(1, 5) == Failure("func_a(1)")
    assert combined(2, 1) == Failure("func_c(3): division by zero")
```

## Turning Exceptions into Results

In `composing.py`, `func_c()` wrapped a risky call in `try`/`except` and returned a `Failure` by hand.
A decorator can capture that pattern.
`@safe` takes a function that raises an exception and gives back one that returns a `Result`,
with the exception as the `Failure` value:

```python
# safe.py
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
#: 42: parsed 42
#: oops: ValueError
```

`parse()` still reads like a normal function that returns an `int`,
but `@safe` has changed its type to `Result[int, Exception]`.
The caller cannot ignore the failure,
because it must unpack the `Result` to reach the number.

The [Decorators](15_Decorators.md) chapter explains how decorators like `@safe` are written, including `functools.wraps`.

`@safe` deserves its own check: a good input becomes a `Success`, and a raised exception becomes a `Failure` holding that exception:

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

## Matching on the Error

Because the error is a value, and is often an exception,
you can pattern-match the `Result` and the exception type together.
Each kind of failure gets its own branch:

```python
# matching_errors.py
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
            return f"{text}: Not a number"
        case Failure(ZeroDivisionError()):
            return f"{text}: Cannot divide by zero"
        case Failure(error):
            return f"{text}: {type(error).__name__}"

if __name__ == "__main__":
    for text in ("4", "0", "OOPS"):
        print(describe(text))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

`parse()` and `reciprocal()` are both wrapped with `@safe`, so `bind()` chains them.
A `ValueError` from a bad number and a `ZeroDivisionError` from dividing by zero arrive as ordinary `Failure` values,
and the `match` tells them apart.

## The returns Library

You do not have to build `Result` yourself.
The [returns](https://github.com/dry-python/returns) library provides a `Result` type with `Success` and `Failure`,
the same `@safe` decorator we just built,
and do-notation that makes combining multiple results read more directly than nested binds.

This style does not replace exceptions everywhere.
Exceptions are still right for truly exceptional conditions,
the ones no caller can reasonably handle,
such as running out of memory or a programming bug.
In some languages, these types of errors are categorized as "panic" errors, and separated from regular exceptions.

Use a `Result` for the failures that are part of a function's normal job:
bad input, a missing file, a value out of range.
Those are not exceptional.
They are expected, and the type should say so.

## Exercises

1.  Add a `func_e()` that returns a `Result[int, str]`,
    and extend the `bind()` chain in `composing_with_bind.py` to include it.
    Confirm a `Failure` from `func_e()` still short-circuits.
2.  Give `Failure` a `map_error()` method that transforms the error it holds,
    leaving a `Success` untouched.
    Use it to add a prefix to every error.
3.  Rewrite `combined` so it collects all the failures instead of stopping at the first one,
    returning `Result[str, list[str]]`.
    Write the tests first.
