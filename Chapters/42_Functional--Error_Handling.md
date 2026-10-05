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
so the type checker forces a caller to check for the failure before reading the answer,
and a reviewer sees it without reading the body.
Control flow stays local.
The failure returns to the immediate caller, the way any value does.
The check at each step is where you handle every failure.

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
but the exception ends the comprehension before it produces the list,
so the assignment to `results` does not run.
To keep the good results you must wrap each call in its own `try`.
That repeats the handling at every call,
the way [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-value-to-check-everywhere)
repeats a range check in every function.

## Return the Error as a Value

The function's return type becomes a union of the answer type and the error type.
A union like this is a *sum type*: a value that is one thing or another.
Python's union carries no tag,
so only the value's runtime type says which side you received.
The error is just another return value, so every result stays in the list:

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

[`match`](13_Techniques--Pattern_Matching.md#builtin-types-and-subclasses)
tells the two cases apart.
But the distinction rests on the types `int` and `str`,
and that dependence is fragile.
If a successful answer is also a string,
`case str(error)` matches it and reports it as an error.
You need something that says "success" or "failure" no matter what types they carry.

## A Result Type

Defining success and failure as types makes them explicit.
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

`Ok` and `Err` are both [records](18_Techniques--Performance.md#record),
`Ok` parameterized over the answer type and `Err` over the error type.
`@final` states that neither can have subclasses,
so no class can inherit from both.
An object the type checker finds to be an `Err` therefore cannot also be an `Ok`,
and a check against one class narrows a `Result` to one side of the union.
`A`, `B`, `E`, and `F` are [type parameters](08_Foundations--Static_Types.md#type-parameters):
placeholders that take concrete types when you use the class.
Here they have no bounds or constraints, so any type can fill them.

Ignore `bind()` for the moment.
The two records and the `Result` alias are enough to report errors.
A function that might fail returns a `Result`.
The signature names both outcomes:

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

### Reaching the Answer

`func_a()`'s return type, `Result[int, str]`,
says it returns an `int` on success or a `str` on failure.
To get the answer, the caller must unpack the `Result`.
`unwrap()`, a name borrowed from Rust, returns the answer an `Ok` holds.
Reading the `answer` field works the same way.
Use whichever name reads better in your own code.
Both exist on `Ok` alone, so the type checker rejects `func_a(i).unwrap()`,
as it rejects using the `Result` as if it were a number.
The only way to the answer is narrowing to one of the two classes,
with `isinstance()` as in `composing.py` below,
or with `match` as in `safe_demo.py`.
`Err` lacks `unwrap()` at runtime as well as under the type checker:

```python
# must_unwrap.py
from exceptions import expected
from result import Err, Ok
from returning_result import func_a

print(hasattr(Ok(1), "unwrap"), hasattr(Err("x"), "unwrap"))
#: True False
with expected(AttributeError):
    func_a(1).unwrap()  # type: ignore
#: [AttributeError] 'Err' object has no attribute 'unwrap'
```

The `# type: ignore` is the point of the listing.
The type checker rejects the bare line,
reporting that `Err[str]` in the union has no `unwrap`,
so a reader who writes that line in their own code sees that report first,
at check time.

`Result` is the same idea as in [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#parse-dont-validate):
put the meaning in the type.
Python's simpler form is `int | None`.
Both force the caller to unpack, but `None` says "no answer,"
while an `Err` carries the reason for the failure.
Use `| None` when absence needs no explanation,
as in a lookup that found nothing.
Use `Result` when the caller may need to act on the reason,
or when several different failures must stay distinguishable,
as [Matching on the Error](#matching-on-the-error) shows below.

### Total Functions

A function like `func_a()` is a *Total Function*,
one whose return type accounts for every outcome it can produce,
success or failure.
If the function raises an exception instead,
the return type does not name that outcome.
Python lets a `Result`-returning function raise an exception as well,
and the type checker cannot report that,
so totality is a discipline the function's author keeps.
The caller's side has the same limit.
A statement that calls the function and discards the `Result` passes the checker.
The type checker catches a misread of a `Result`, but ignoring one is up to you.
The listing holds one gap of each kind:

```python
# totality_gap.py
from result import Result
from returning_result import func_a

func_a(1)  # Result discarded; nothing complains

def lies(i: int) -> Result[int, str]:
    raise RuntimeError("not total after all")
    # ty accepts this: a function that always
    # raises satisfies any declared return type.
```

`func_a(1)` returns a `Result` that the listing discards,
and `lies()` raises an exception instead of returning the `Result` its signature declares.
The type checker accepts both.

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

`composed()` returns early when a step returns an `Err`.
The check names `Err`, one of the two concrete classes,
because `Result` is a `type` alias rather than a class.
The type checker rejects `isinstance(a, Result)`,
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
    _ = 1 / (i - 3)  # Raises when i == 3
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

The two `composed()` functions succeed and fail on the same inputs,
and the exception version is shorter, but its signature says less.
`-> int` names no failure, where `-> Result[int, str]` names one.
The failure also disappears when the `except` clause ends,
whereas `sum_type.py` at the start of this chapter keeps every result in a list.

## Composing With bind

`bind()` is the sequence `composing.py` repeats at every step, written once.
Look again at the two `bind()` methods in `result.py`.
On an `Ok`, `bind()` passes the answer to the next function.
On an `Err`, `bind()` skips the function and returns the `Err`,
the same failure.
The two signatures differ because `Err` holds no answer to pass to the next step.
`Err.bind()` therefore accepts a callable with any parameter list,
and its return type is `Err[E]`, because it returns `self`.
An `Err` anywhere in a chain skips the rest of the steps,
because each later `bind()` returns that same `Err`:

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
`composed()` has no `isinstance()` check and no early return left.

Functional programmers have a name for a type with a way to wrap a plain value
(`Ok()` here) and this chaining operation: a *monad*.
You can use `bind()` without the word, but the word names a reusable shape.
`Maybe` chains a value that might be absent,
`Result` chains one that might have failed,
and an async container chains one whose computation has not finished yet,
all with the same `bind()`.

One mistake to expect when you start chaining:
`bind()` requires each step to return a `Result`.
If you pass it a plain function, say `.bind(str)`,
the type checker rejects that call, because `str` returns a `str`,
and `bind()` expects a `Result`.
To chain a plain function, wrap its return value: `.bind(lambda x: Ok(str(x)))`.
Libraries like `returns` name that pattern `map()`,
a sibling of `bind()` for steps that cannot fail.
Exercise 2's `map_error()` is the same idea applied to the error side.

A second mistake: mixing error types.
`Result[A, E]` names one error type for the whole chain.
If one step's `Err` carries a type different from an earlier step's,
the chain returns a union of both types,
and that union is wider than the annotation you wrote.
Keep a chain's error type the same at every step,
or annotate the chain with the union each step can produce.

Because failures are values, you can assert on them with no `pytest.raises()`.
The tests check that `unwrap()` returns the answer,
and that `bind()` chains a success and short-circuits a failure.
The last assertion uses `is` rather than `==`,
proving `bind()` returns the original `Err` object rather than an equal copy:

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

`test_composing.py` confirms that the hand-written and `bind()` versions agree on the five inputs the demos use:

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

`bind()` passes one value from each step to the next.
When you have several independent inputs,
nest the binds so each answer stays in scope for the next step.

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

Each lambda's parameter is the previous step's answer.
The nesting keeps every earlier answer in scope,
so `a` is still visible inside the inner lambda that receives `b`.
A flat sequence of `bind()` calls drops the earlier answer from scope,
because each step's function receives one argument, the previous answer.

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

An `Err` anywhere short-circuits to the end.
`(7, 5)` is the one input of the four that passes all three steps,
so `add()` runs for that input alone.

Short-circuiting is right for a dependent chain,
where each step needs the previous step's answer,
as in `composing_with_bind.py` above.
`func_a()`, `func_b()`,
and `func_c()` in `combining.py` take independent inputs,
so stopping at the first `Err` discards whatever the later steps would have found
(see exercise 3).
The exception in `exceptions_lose_data.py` does the same to `func_a(4)`,
which does not run.

Three inputs need three levels of nesting,
and each input you add nests one level deeper.
[The returns Library](#the-returns-library)
at the end of this chapter offers do-notation,
a flatter alternative to this nesting.

`test_combining.py` confirms that `combined()` returns the answer,
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

In `composing.py`, `func_c()` puts a `try`/`except` around a division that can raise a `ZeroDivisionError` and returns an `Err` by hand.
A decorator can capture that pattern.
`@safe` takes a function that raises an exception and produces one that returns a `Result`,
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
but `@safe` has changed its return type to `Result[int, Exception]`,
so the caller must unpack the `Result` to reach the number.
That error type, `Exception`, is the base of the ordinary exception hierarchy,
so the signature says that something can go wrong and not what,
which is all a bare `except Exception` says.
`@safe` names `Exception` because it writes one `try`/`except` for every function it wraps,
and the base class is the one type that covers whatever those functions raise.
A wrapper written by hand can be narrower.
`func_c()` in `composing.py` catches `ZeroDivisionError` alone,
and a `parse()` that catches `ValueError` the same way can return `Result[int, ValueError]`.
Write the wrapper yourself when the narrower type matters more than the convenience.

`@safe` catches `Exception`,
which is every ordinary failure the wrapped function can produce,
including the ones that are defects rather than expected outcomes.
If you misspell a name inside the wrapped function,
`@safe` returns the resulting `NameError` as an ordinary `Err`,
which looks the same as bad input.
The version in `safe.py` is deliberately small.
A production version takes the exception types to catch as an argument and lets the rest propagate.
Letting the rest propagate keeps the distinction that [Which Failures Get a Result](#which-failures-get-a-result)
draws: a failure the caller can handle versus a bug the caller cannot.

`@safe` changes the return type and keeps what the function accepts.
The `**P` parameter carries the wrapped function's whole parameter list through,
so `parse("42")` type-checks and the checker rejects `parse(42)`.
`**P` is the technique for [maintaining the wrapped interface](14_Techniques--Decorators.md#p-and-r-keep-the-static-interface),
and [Decorators](14_Techniques--Decorators.md)
explains how to write decorators like `@safe`, including `functools.wraps`.

The tests for `@safe` check that a good input becomes an `Ok`,
and that a raised exception becomes an `Err` holding that exception:

```python
# test_safe.py
from result import Err, Ok
from safe_demo import parse

def test_good_input_becomes_an_ok() -> None:
    assert parse("42") == Ok(42)

def test_exception_becomes_an_err() -> None:
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

def compute(text: str) -> Result[float, Exception]:
    return parse(text).bind(reciprocal)

def describe(
    text: str, result: Result[float, Exception]
) -> str:
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
    texts = ("4", "0", "OOPS")
    # Every Result computed first, matched after:
    results = [compute(text) for text in texts]
    for text, result in zip(texts, results):
        print(describe(text, result))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
```

`@safe` wraps both `parse()` and `reciprocal()`, so `bind()` chains them.
A `ValueError` from a bad number and a `ZeroDivisionError` from dividing by zero each become the `error` field of an ordinary `Err`.
`compute()` returns a `Result`, a value the caller keeps after the call returns,
so the comprehension computes all three results before `describe()` matches any of them.
A raised exception would have ended the comprehension at the first failure.

The parentheses in `Err(ValueError())` do the type test.
Without them, `case Err(ValueError):` is a [capture](13_Techniques--Pattern_Matching.md#a-bare-name-captures-a-dotted-name-compares).
It matches every `Err` and binds the error to a new local named `ValueError`.
Python compiles that `case` and the type checker accepts it,
so `describe()` would answer "Not a number" for a `ZeroDivisionError`.

## Attaching Context to an Exception {#attaching-context-to-an-exception}

An exception's message says what went wrong but not where.
`invalid literal for int() with base 10: 'no'` is accurate and leaves the reader asking:
which setting, which field, which row of the file?
The frame that has that answer is rarely the frame that raised the exception.
A handler far enough up the stack to report the failure cannot see the locals that would explain it.

Most code catches the exception and raises a new one with a better message.
The new exception replaces the original type,
so a caller who wants the original must read it from the new exception's `__cause__`
(set by `raise New(...) from e`) or `__context__`
(set when a handler raises an exception without `from`).
`BaseException.add_note()`, added in Python 3.11,
improves the message and keeps the exception.
It appends a line to the existing message, and the traceback prints that line:

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

The bare `raise` re-raises the same object, so the exception keeps its type,
`ValueError`, and its original traceback.
The listing prints with `traceback.format_exception_only()`,
which renders the message and the notes and leaves out the file paths a full traceback carries.

Notes accumulate.
As the stack unwinds,
each `except` clause along the way can add a line built from its own frame's locals,
which the raiser's frame does not have.
`add_note()` appends each note to a list, `__notes__`,
which the first call creates.
The type checker treats `__notes__` as always present, because typeshed,
the collection of type declarations for the standard library that every checker reads,
declares it on `BaseException`.
Reading `__notes__` before any `add_note()` call therefore type-checks,
and then raises an `AttributeError` at runtime.

Context matters more under a `Result` than in ordinary exception code,
because the `Result` keeps the exception as a value rather than propagating it.
Nothing prints a traceback for an `Err` stored in a list.
The exception inside still holds its `__traceback__`,
but the `except` clause that caught it returned it as a value,
so the exception reaches no handler.
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
in the one frame that has both the exception and the field name.
Code that reads the `Err` later can report which field failed without the frame that parsed it.
The note is the chapter's opening argument, applied one level down.
`Err` says the call failed, the exception says what went wrong,
and a note says which piece of work produced it.

The `Err` branch reads `error.__notes__`,
and that read type-checks because the `match` narrowed the `Result` to `Err`.
The narrowing works because `Result` is a union of exactly two classes,
and it works the same way with `isinstance()`.
Reading `error.__notes__` without a default is safe here only because `parse_field()` adds a note on every failure.
An exception that arrives from code you did not write may carry no notes,
so read `__notes__` with `getattr(error, "__notes__", [])`.

## The returns Library

A library can supply `Result` for you.
The [returns](https://github.com/dry-python/returns)
library provides a `Result` type whose two cases are `Success` and `Failure`,
the same `@safe` decorator you built in `safe.py`, and do-notation,
which combines multiple results in one flat expression instead of nested binds.
Its `@safe` takes an `exceptions` argument naming the types to catch,
the production form that exercise 4 builds.

## Which Failures Get a Result

A `Result` does not replace every exception.
Exceptions remain the right tool for truly exceptional conditions:
running out of memory, a programming bug,
anything a caller cannot reasonably handle.
Rust and Go call these errors *panics*,
and keep them apart from the errors a function returns as values.

Use a `Result` for the failures that are part of a function's normal job:
bad input, a missing file, a value out of range.
Those are not exceptional.
They are routine, and the type should say so.

You can now write a function whose signature admits it can fail,
and chain three of them without a single `try` in the calling code.
The chain returns either an answer or the first failure,
and the type checker makes a caller tell the two apart.
[Confidence](43_Functional--Confidence.md)
examines what this discipline lets you claim,
and [Effect Management](44_Effects--Effect_Management.md#converting-effectful-to-pure)
reuses this `Result` machinery to convert Effects.

## Exercises

This chapter's [solutions](../Solutions/42_Functional--Error_Handling/)
give a hint, usually the shape of the code, and a full answer for each exercise.

1.  Add a `func_d()` that returns a `Result[int, str]`,
    and extend the `bind()` chain in `composing_with_bind.py` to include it.
    Put it in the middle of the chain rather than at the end,
    so an `Err` from it has a later step to skip,
    and confirm that the step does not run.
2.  Give `Err` a `map_error()` method that transforms the error it holds,
    leaving an `Ok` untouched
    (for chains to keep working, `Ok` needs its own `map_error()` that returns `self`).
    Use it to add a prefix to every error.
3.  Rewrite `combined()` so it collects all the failures instead of stopping at the first one,
    returning `Result[str, list[str]]`.
    Write the tests first.
4.  Change `@safe` so it takes the exception types it should catch,
    as in `@safe(ValueError)`, and lets anything else propagate.
    Show that a `TypeError` raised inside the wrapped function now propagates,
    and `@safe` no longer returns it as an `Err`.
5.  Write `load_setting(name, text)` that returns `Result[int, Exception]` and attaches a note naming the setting.
    Chain two of them with `bind()` and print the notes from whichever one failed.
    Does the successful call carry a note?
    Why or why not?
6.  Rewrite `func_a()`, `func_b()`,
    and `func_c()` to return `int | None` instead of `Result[int, str]`,
    and adjust `composing.py` to match.
    What can the caller still tell about which of the three steps failed?
