# Error Handling

> A call can fail, and nothing in its signature says so.
> Returning the failure as a value puts it in the signature,
> where the caller must deal with it.

[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes a value carry a guarantee.
This chapter does the same for errors.
The return value is either the answer or the failure, and its type says so.

Exceptions are Python's default error mechanism, and they have three drawbacks.
An exception unwinds the stack, so it discards any work done so far.
It does not appear in the function's return type,
so the signature reads as though the call always succeeds.
And forgetting to handle one is easy.

Returning the failure as a value addresses all three.
Failure appears in the return type,
so a reviewer sees it without reading the body.
The type checker also forces a caller to check for the failure before reading the answer.

Control flow also stays local.
The failure returns to the immediate caller, the way any value does.
A failure in one call therefore leaves the results of the others intact.
Each caller handles the failure next to the call that produced it.

This material comes from my PyCon 2024 talk,
[Functional Error Handling](https://github.com/BruceEckel/functional_error_handling).

## Exceptions Discard Partial Calculations

[Functional Toolkits](41_Functional--Toolkits.md#choosing-from-the-toolkits)
ends by asking what a pipeline of pure stages does when one stage fails.
A comprehension is the smallest such pipeline.
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
but the exception ends the comprehension before it produces the list.
To keep the good results you must wrap each call in its own `try`.
That repeats the handling at every call,
the way [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-value-to-check-everywhere)
repeats a range check in every function.

## Return the Error as a Value

The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type*: a value that is one thing or another.
Python's union carries no tag,
so only the value's runtime type says which side you received.
The error is an ordinary return value, so every result stays in the list:

```python
# sum_type.py

def func_a(i: int) -> int | str:
    if i == 3:
        # The error, returned as a value
        return f"func_a({i})"
    return i

results = [func_a(i) for i in range(5)]
for result in results:
    match result:
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

[`match`](13_Techniques--Pattern_Matching.md#builtin-types-and-subclasses)
tells the two cases apart.
But the distinction depends on the answer and the error having different types,
here `int` and `str`.
If a successful answer is also a string,
`case str(error)` matches it and reports it as an error.
You need a tag that says "success" or "failure,"
whatever types the answer and the error have.

## A Result Type

Defining success and failure as types puts them in the signature.
`Ok` wraps an answer, `Err` wraps an error,
and `Result` is the union of the two.
The value's class is now the tag that tells the two cases apart,
so the union stays unambiguous whatever the two sides carry.
Other languages call this a *tagged* or *discriminated* union.
`Result` is useful beyond this chapter,
so it lives in `utils/` and any chapter can import it:

```python
# utils/result.py
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

@final
@record
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        return self  # Pass the failure forward unchanged

type Result[A, E] = Ok[A] | Err[E]
```

`Ok` and `Err` are both [records](18_Techniques--Performance.md#record).
`@final` states that neither can have subclasses,
so no class can inherit from both.
The type checker therefore knows that an `Err` cannot also be an `Ok`,
so a check against one class narrows a `Result` to one side of the union.

`A`, `B`, `E`, and `F` are [type parameters](08_Foundations--Static_Types.md#type-parameters):
placeholders for concrete types.
`Ok[A]` declares `A` on its class and `Err[E]` declares `E`,
so those two take concrete types when you use the class.
Each `bind()` declares its own type parameters after its name.
Those take concrete types at each call.
The `E` of `Ok.bind()` is a separate parameter from the `E` that `Err` declares.
Here the type parameters have no bounds or constraints,
so any type can fill them.

Ignore `bind()` for the moment.
The two records and the `Result` alias are enough to report errors.
A function that might fail returns a `Result`.
The signature specifies both outcomes:

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

### Reaching the Answer

To get the answer, the caller must unpack the `Result`.
`unwrap()`, a name borrowed from Rust, returns the answer an `Ok` holds.
Reading the `answer` field returns the same value.
Use whichever name reads better in your own code.

`unwrap()` and the `answer` field exist on `Ok` alone,
so the type checker rejects `func_a(i).unwrap()`,
as it rejects using the `Result` as if it were a number.
Apart from `bind()`,
the only way to the answer is narrowing to one of the two classes,
with `isinstance()` as in `composing.py` below,
or with `match` as in `safe_demo.py`.

The runtime agrees with the type checker.
Calling `unwrap()` on an `Err` raises an `AttributeError`:

```python
# must_unwrap.py
from exceptions import expected
from returning_result import func_a

with expected(AttributeError):
    func_a(1).unwrap()  # type: ignore
#: [AttributeError] 'Err' object has no attribute 'unwrap'
```

The `# type: ignore` silences the type checker so the listing can reach the runtime failure.
If you delete the comment, the type checker rejects the line,
reporting that `Err[str]` in the union has no `unwrap`.
If you write that line in your own code,
the type checker therefore reports it at check time,
before any `AttributeError` at runtime.

`Result` is the same idea as in [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#parse-dont-validate):
put the meaning in the type.
Python's simpler form is `int | None`.
Both force the caller to unpack, but `None` says "no answer,"
while an `Err` carries the reason for the failure.

Use `| None` when the caller needs to know whether an answer exists,
as in a lookup by key.
Use `Result` when the caller may need to act on the reason,
or when several different failures must stay distinguishable,
as [Matching on the Error](#matching-on-the-error) shows below.

### Total Functions

A function like `func_a()` is a *Total Function*,
one whose return type accounts for every outcome it can produce,
success or failure.
If the function raises an exception instead,
the return type does not specify that outcome.
Python lets a `Result`-returning function raise an exception as well,
and the type checker accepts it.
Totality is therefore a discipline the function's author keeps.

The caller's side has the same limit.
A statement that calls the function and discards the `Result` passes the checker.
The type checker reports a read of the answer before narrowing,
but noticing an ignored `Result` is up to you.
The listing shows both limits:

```python
# totality_gap.py
from exceptions import expected
from result import Result
from returning_result import func_a

func_a(1)  # Result discarded; nothing complains

def lies(i: int) -> Result[int, str]:
    raise RuntimeError("not total after all")

with expected(RuntimeError):
    lies(1)
#: [RuntimeError] not total after all
```

The type checker accepts both the discarded `Result` and `lies()`.
Discarding a return value is legal Python.
The checker compares a declared return type with the value of each `return` statement,
so a function that always raises an exception satisfies any return type.

## Composing by Hand

Real programs chain steps.
With a `Result`, each step can fail,
so you must check each call before the next one runs.

You can catch an exception from existing code and turn it into an `Err`,
so the failure becomes data rather than control flow.
`func_c()` does that with a `ZeroDivisionError`.

`steps.py` gathers the three steps the rest of the chapter chains,
so a listing imports all three from one module.
The module imports `func_a()` and names it in [`__all__`](06_Foundations--Modules_and_Packages.md#what-a-module-exports)
beside its own two functions.
Listing an imported name in `__all__` declares it part of the module's public interface:

```python
# steps.py
from result import Err, Ok, Result
from returning_result import func_a

__all__ = ["func_a", "func_b", "func_c"]

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
```

`composed()` runs the three steps in order and checks each `Result` with `isinstance()`:

```python
# composing.py
from result import Err, Result
from steps import func_a, func_b, func_c

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

`Result` is a `type` alias rather than a class,
so the type checker rejects `isinstance(a, Result)`,
and at runtime the call raises a `TypeError`.

`composed()` works, and it keeps errors as values,
but every step is the same sequence: call, check for `Err`, return early,
unwrap, go on.
Written with exceptions and one `try` at the top,
the same composition is shorter:

```python
# composing_exceptions.py

def func_a(i: int) -> int:
    if i == 1:
        raise ValueError(f"func_a({i})")
    return i

def func_b(i: int) -> int:
    if i == 2:
        raise ValueError(f"func_b({i})")
    return i

def func_c(i: int) -> int:
    _ = 1 / (i - 3)  # Raises ZeroDivisionError when i == 3
    return i

def composed(i: int) -> int:
    return func_c(func_b(func_a(i)))

if __name__ == "__main__":
    for i in range(5):
        try:
            print(i, composed(i))
        except (ValueError, ZeroDivisionError) as e:
            print(i, f"failed: {e}")
#: 0 0
#: 1 failed: func_a(1)
#: 2 failed: func_b(2)
#: 3 failed: division by zero
#: 4 4
```

The two `composed()` functions succeed and fail on the same inputs.
The exception version is shorter, but its signature says less.
`-> int` states the success type alone,
where `-> Result[int, str]` states the failure type as well.

In the exception version, the caller receives the error through `e`,
the name the `except` clause binds.
Python deletes `e` when that clause ends,
whereas `sum_type.py` at the start of this chapter keeps every result in a list.

## Composing With bind

`bind()` is one copy of the sequence that `composing.py` repeats at every step.
Look again at the two `bind()` methods in `result.py`.
On an `Ok`, `bind()` passes the answer to the next function.
On an `Err`, `bind()` skips the function and returns the `Err` unchanged.

The two `bind()` signatures differ because the next step takes an answer,
whereas an `Err` holds an error.
`Err.bind()` therefore accepts a callable with any parameter list,
and its return type is `Err[E]`, because it returns `self`.

An `Err` anywhere in a chain skips the rest of the steps,
because each later `bind()` returns that same `Err`:

```python
# composing_with_bind.py
from result import Result
from steps import func_a, func_b, func_c

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

`bind()` replaces the `isinstance()` checks and early returns of `composing.py` with a chain of calls.

Functional programmers call a type a *monad* when it has two operations:
one that wraps a plain value (`Ok()` here) and this chaining operation.
You can use `bind()` without the word,
but the word names a structure that many types share.
`Maybe` chains a value that might be absent,
`Result` chains one that might have failed,
and an async container chains one whose computation is still running,
all with the same `bind()`.

One mistake to expect when you start chaining:
`bind()` requires each step to return a `Result`.
If you pass it a plain function, say `.bind(str)`,
the type checker rejects that call, because `str` returns a `str`,
and `bind()` expects a `Result`.
To chain a plain function, wrap its return value: `.bind(lambda x: Ok(str(x)))`.
Libraries like `returns` name that pattern `map()`,
a sibling of `bind()` for steps that always succeed.
Exercise 2's `map_error()` applies a plain function to the error inside an `Err`,
as `map()` does to the answer inside an `Ok`.

A second mistake: mixing error types.
`Result[A, E]` specifies one error type for the whole chain.
If one step's `Err` carries a type different from an earlier step's `Err`,
the chain returns a union of both types,
and that union is wider than the annotation you wrote.
Keep a chain's error type the same at every step,
or annotate the chain with the union each step can produce.

Because failures are values,
the tests assert on them with ordinary comparisons in place of `pytest.raises()`.
The tests check that `unwrap()` returns the answer,
and that `bind()` chains a success and short-circuits a failure:

```python
# test_result.py
from result import Err, Ok

def test_unwrap_returns_the_answer() -> None:
    assert Ok(5).unwrap() == 5

def test_bind_chains_a_success() -> None:
    assert Ok(1).bind(lambda x: Ok(x + 1)) == Ok(2)

def test_bind_short_circuits_a_failure() -> None:
    failure: Err[str] = Err("boom")
    assert failure.bind(lambda x: Ok(x + 1)) is failure
```

The assertion in `test_bind_short_circuits_a_failure()` uses `is`,
proving `bind()` returns the original `Err` object rather than an equal copy.

A parametrized test confirms that the hand-written and `bind()` versions agree on the five inputs the demos use:

```python
# test_composing.py
import pytest
from composing import composed as composed_manual
from composing_with_bind import composed as composed_bind

@pytest.mark.parametrize("i", range(5))
def test_manual_and_bind_agree(i: int) -> None:
    assert composed_manual(i) == composed_bind(i)
```

## Combining Multiple Results

`bind()` passes one answer from each step to the next.
When you have several independent inputs,
nest the binds so each answer stays in scope for every later step:

```python
# combining.py
from result import Ok, Result
from steps import func_a, func_b, func_c

def add(a: int, b: int, c: int) -> str:
    return f"add({a} + {b} + {c}): {a + b + c}"

def combined(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: func_c(i + j).bind(
                lambda c: Ok(add(a, b, c)))))

if __name__ == "__main__":
    for args in [(1, 5), (7, 2), (2, 1), (1, 2), (7, 5)]:
        print(args, combined(*args))
#: (1, 5) Err(error='func_a(1)')
#: (7, 2) Err(error='func_b(2)')
#: (2, 1) Err(error='func_c(3): division by zero')
#: (1, 2) Err(error='func_a(1)')
#: (7, 5) Ok(answer='add(7 + 5 + 12): 24')
```

Because the nesting keeps every earlier answer in scope,
`a` and `b` are still visible inside the innermost lambda that receives `c`.
A flat sequence of `bind()` calls drops the earlier answers from scope,
because each step's function receives one argument, the previous answer.

Short-circuiting is right for a dependent chain,
where each step needs the previous step's answer,
as in `composing_with_bind.py` above.
In `combining.py`, the three steps take their inputs from `i` and `j` rather than from an earlier step's answer,
so stopping at the first `Err` discards whatever the later steps would have found.
For `(1, 2)`, `func_b(2)` and `func_c(3)` fail too.
The result reports `func_a(1)` alone (see exercise 3).
The exception in `exceptions_lose_data.py` does the same.
It ends the comprehension at `func_a(3)`, before `func_a(4)` runs.

Three steps need three levels of nesting,
and each step you add nests one level deeper.
[The returns Library](#the-returns-library)
later in this chapter offers do-notation, a flatter alternative to this nesting.

A second parametrized test confirms that `combined()` returns the answer,
or the first failure in the chain:

```python
# test_combining.py
import pytest
from combining import combined
from result import Err, Ok, Result

@pytest.mark.parametrize("i, j, expected", [
    (7, 5, Ok("add(7 + 5 + 12): 24")),
    (1, 5, Err("func_a(1)")),
    (7, 2, Err("func_b(2)")),
    (2, 1, Err("func_c(3): division by zero")),
    (1, 2, Err("func_a(1)")),
])
def test_combined_returns_answer_or_first_failure(
    i: int, j: int, expected: Result[str, str]
) -> None:
    assert combined(i, j) == expected
```

## Turning Exceptions into Results

In `steps.py`, `func_c()` wraps a division in a `try`/`except` and returns an `Err` from the `except` clause when the division raises a `ZeroDivisionError`.
A decorator captures that pattern.
`@safe` takes a function that can raise an exception and produces one that returns a `Result`,
with the exception as the error the `Err` wraps.
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

`@safe` goes on any function that can raise an exception:

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
but `@safe` changes its return type to `Result[int, Exception]`,
so the caller must unpack the `Result` to reach the number.

That error type, `Exception`, is the base of the ordinary exception hierarchy.
The signature therefore says that something can go wrong and not what,
which is all an `except Exception` clause says.
`@safe` catches `Exception` because it writes one `try`/`except` for every function it wraps,
and the base class is the narrowest type that covers every ordinary exception those functions raise.
A `try`/`except` written for one function can be narrower.
`func_c()` in `steps.py` catches `ZeroDivisionError` alone,
and a `parse()` that catches `ValueError` the same way can return `Result[int, ValueError]`.
Write the wrapper yourself when the caller needs to know which exception type the `Err` holds,
and use `@safe` when `Exception` tells the caller enough.

`Exception` covers every ordinary failure the wrapped function can produce,
including the ones that are defects rather than expected outcomes.
If you misspell a name inside the wrapped function,
`@safe` returns the resulting `NameError` as an ordinary `Err`,
which looks the same as bad input.
The version in `safe.py` is deliberately small.
A production version takes the exception types to catch as an argument and lets the rest propagate.
Letting the rest propagate keeps the distinction that [Which Failures Get a Result](#which-failures-get-a-result)
draws: a failure the caller can handle versus a bug the caller cannot.

`@safe` changes the return type and keeps what the function accepts.
The `**P` parameter forwards the wrapped function's whole parameter list to `wrapper()`,
so `parse("42")` type-checks and the checker rejects `parse(42)`.
`**P` is the technique for [maintaining the wrapped interface](14_Techniques--Decorators.md#p-and-r-keep-the-static-interface).
[Decorators](14_Techniques--Decorators.md)
explains how to write decorators like `@safe`, including `functools.wraps()`.

The tests for `@safe` check that a good input becomes an `Ok`,
and that a raised exception becomes an `Err` holding that exception:

```python
# test_safe.py
from result import Err, Ok
from safe_demo import parse

def test_good_input_becomes_an_ok() -> None:
    assert parse("42") == Ok(42)

def test_exception_becomes_an_err() -> None:
    result = parse("oops")
    assert isinstance(result, Err)
    assert isinstance(result.error, ValueError)
```

## Matching on the Error

Because the error is a value, and is often an exception,
you can pattern-match the `Result` and the exception type together.
Each kind of failure gets its own branch:

```python
# matching_errors.py
from result import Err, Ok, Result
from safe import safe
from safe_demo import parse

@safe
def reciprocal(n: int) -> float:
    return 1 / n

def compute(text: str) -> Result[float, Exception]:
    return parse(text).bind(reciprocal)

def describe(result: Result[float, Exception]) -> str:
    match result:
        case Ok(answer):
            return str(answer)
        case Err(ValueError()):
            return "Not a number"
        case Err(ZeroDivisionError()):
            return "Cannot divide by zero"
        case Err(error):
            return type(error).__name__

if __name__ == "__main__":
    results = {text: compute(text)
               for text in ("4", "0", "OOPS")}
    for text, result in results.items():
        print(f"{text}: {describe(result)}")
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

`@safe` wraps both `parse()`, imported from `safe_demo.py`, and `reciprocal()`,
so each returns a `Result` and `bind()` chains them.

`compute()` returns a `Result`, a value the caller keeps after the call returns,
so the dict comprehension collects all three results before `describe()` matches any of them.
A raised exception ends the comprehension at the first failure.

The parentheses in `Err(ValueError())` do the type test.
Written bare, `case Err(ValueError):` is a [capture](13_Techniques--Pattern_Matching.md#a-bare-name-captures-a-dotted-name-compares).
It matches every `Err` and binds the error to a new local named `ValueError`,
so `describe()` answers "Not a number" for a `ZeroDivisionError`.
Python compiles that `case`, and the type checker accepts it.

## Attaching Context to an Exception {#attaching-context-to-an-exception}

An exception's message says what went wrong but not where.
`invalid literal for int() with base 10: 'no'` is accurate and leaves the reader asking:
which setting, which field, which row of the file?
The stack frame that has that answer is usually a caller of the one that raised the exception.
When a handler sits far enough up the stack to report the failure,
the locals that explain it are out of reach.

Most code catches the exception and raises a new one with a better message.
The new exception replaces the original type.
A caller who wants the original must read it from the new exception's `__cause__`,
which `raise New(...) from e` sets, or from `__context__`,
which Python sets when a handler raises an exception without `from`.
`BaseException.add_note()`, added in Python 3.11,
adds context to the original exception instead of replacing it.
It attaches a line that the traceback prints after the original message:

```python
# add_note.py
import traceback

def parse_seconds(text: str) -> int:
    try:
        return int(text)
    except ValueError as e:
        e.add_note("expected a whole number of seconds")
        raise

def read_setting(name: str, text: str) -> int:
    try:
        return parse_seconds(text)
    except ValueError as e:
        e.add_note(f"setting {name!r} was {text!r}")
        raise

try:
    read_setting("timeout", "no")
except ValueError as e:
    print("".join(traceback.format_exception_only(e)),
          end="")
#: ValueError: invalid literal for int() with base 10: 'no'
#: expected a whole number of seconds
#: setting 'timeout' was 'no'
```

Each bare `raise` re-raises the same object, so the exception keeps its type,
`ValueError`, and its original traceback.
The listing prints with `traceback.format_exception_only()`,
which renders the message and the notes and leaves out the file paths a full traceback carries.

Notes accumulate.
As the exception propagates,
each `except` clause that catches and re-raises it can add a line built from its own stack frame's locals.
The stack frame that raised the exception cannot see those locals.
In `add_note.py`, `read_setting()` builds its note from its own parameter `name`,
which `parse_seconds()` never receives.

`add_note()` appends each note to a list, `__notes__`,
which the first call creates.
The type checker treats `__notes__` as always present,
because typeshed declares it on `BaseException`.
Typeshed is the collection of type declarations for the standard library that every checker reads.
Reading `__notes__` before any `add_note()` call therefore type-checks,
and then raises an `AttributeError` at runtime.

Context matters more under a `Result` than in ordinary exception code,
because the `Result` keeps the exception as a value rather than propagating it.
The exception inside an `Err` still holds its `__traceback__`,
but the traceback of an `Err` stored in a list stays out of sight until your code prints it.
The `except` clause that caught the exception returns it as a value,
so every caller above that clause receives an `Err`, an ordinary return value.
No handler above that clause catches the exception,
so none can add a note from its own stack frame.
The exception must carry the context it needs before it becomes an `Err`:

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

results = [parse_field("age", "42"),
           parse_field("size", "oops")]
for result in results:
    match result:
        case Ok():
            print(result)
        case Err(error):
            print(type(error).__name__)
            for note in error.__notes__:
                print(f"  {note}")
#: Ok(answer=42)
#: ValueError
#:   field 'size' received 'oops'
```

`parse_field()` adds the note before it returns the exception as a value,
in the one stack frame that has both the exception and the field name.
The loop reads each `Result` after `parse_field()` has returned,
and it never sees a field name.
It still reports which field failed,
because the `Err` holds the exception and the exception holds the note.

The note applies the chapter's opening argument to the exception inside the `Err`.
`Err` says the call failed, the exception says what went wrong,
and a note says which piece of work produced the exception.

The `Err` branch reads `error.__notes__`, and that read type-checks.
The `match` narrows the `Result` to `Err[Exception]`,
so the type checker infers that `error` is an `Exception`.
Typeshed declares `__notes__` on `Exception`'s base class, `BaseException`.
`isinstance(result, Err)` narrows `result` to `Err[Exception]` too.

Reading `error.__notes__` is safe here because `parse_field()` adds a note on every failure.
An exception from someone else's code has a `__notes__` attribute only if something called `add_note()` on it,
so read `__notes__` with `getattr(error, "__notes__", [])`.

## The returns Library

A library can supply `Result` for you.
The [returns](https://github.com/dry-python/returns)
library provides a `Result` type whose two cases are `Success` and `Failure`,
a `@safe` decorator like the one in `safe.py`, and do-notation,
which combines multiple results in one flat expression instead of nested binds.
Its `@safe` takes an `exceptions` argument specifying the types to catch,
the production form that exercise 4 builds.

## Which Failures Get a Result

Exceptions remain the right tool for truly exceptional conditions:
running out of memory, a programming bug,
anything a caller cannot reasonably handle.
Rust and Go call these errors *panics*,
and keep them apart from the errors a function returns as values.

Use a `Result` for failures that are part of a function's normal job: bad input,
a missing file, a value out of range.
Those are not exceptional.
They are routine, and the type should say so.

You can now write a function whose signature declares that it can fail,
and chain three of them without a single `try` in the calling code.
The chain returns either an answer or the first failure.
The type checker makes a caller tell the two apart.
[Confidence](43_Functional--Confidence.md)
examines what this discipline lets you claim,
and [Effect Management](44_Effects--Effect_Management.md#converting-effectful-to-pure)
imports this chapter's `Result` and `@safe` to convert Effects.

## Exercises

Try each exercise before opening its [solution](../Solutions/42_Functional--Error_Handling/).

1.  Add a `func_d()` that returns a `Result[int, str]`,
    and extend the `bind()` chain in `composing_with_bind.py` to include it.
    Put it in the middle of the chain rather than at the end,
    so an `Err` from it has a later step to skip,
    and confirm that the later step does not run.
2.  Give `Err` a `map_error()` method that transforms the error it holds,
    leaving an `Ok` as it is
    (for chains to keep working, `Ok` needs its own `map_error()` that returns `self`).
    Use it to add a prefix to every error.
3.  Rewrite `combined()` so it collects all the failures instead of stopping at the first one,
    returning `Result[str, list[str]]`.
    Write the tests first.
4.  Change `@safe` so it takes the exception types it should catch,
    as in `@safe(ValueError)`, and lets anything else propagate.
    Show that a `TypeError` raised inside the wrapped function now propagates,
    where the original `@safe` returned it as an `Err`.
5.  Write `load_setting(name, text)` that returns `Result[int, Exception]` and attaches a note naming the setting.
    Chain two of them with `bind()` and print the notes from whichever one failed.
    Does the successful call carry a note?
    Why or why not?
6.  Rewrite `func_a()`, `func_b()`,
    and `func_c()` to return `int | None` instead of `Result[int, str]`,
    and adjust `composing.py` to match.
    What can the caller still tell about which of the three steps failed?
