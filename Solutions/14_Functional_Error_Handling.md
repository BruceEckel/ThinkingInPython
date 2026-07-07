# Functional Error Handling: Solutions

## 1. A fourth step, `func_e()`, added to the `bind()` chain

```python
# exercise_1.py
from __future__ import annotations
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

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Failure(f"func_b({i})")
    return Success(i)

def func_c(i: int) -> Result[int, str]:
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        return Failure(f"func_c({i}): {e}")
    return Success(i)

def func_e(i: int) -> Result[int, str]:
    if i == 4:
        return Failure(f"func_e({i})")
    return Success(i * 10)

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c).bind(func_e)

for i in range(5):
    print(i, composed(i))
#: 0 Success(answer=0)
#: 1 Failure(error='func_a(1)')
#: 2 Failure(error='func_b(2)')
#: 3 Failure(error='func_c(3): division by zero')
#: 4 Failure(error='func_e(4)')
```

Adding a fourth `.bind(func_e)` needed no change to `Result`, `Success`,
or `Failure`. `i == 4` reaches `func_e()` only because it survived
`func_a`, `func_b`, and `func_c` (unlike `1`, `2`, and `3`, which fail
earlier and never even reach `func_e`), and `func_e(4)`'s `Failure`
then propagates unchanged through nothing further, since it is the
last step in the chain. Every input from `0` to `4` now fails at
exactly one step, which happens to be a different step each time,
demonstrating that a chain of any length short-circuits at its first
failure, wherever that falls.

## 2. `Failure.map_error()`

```python
# exercise_2.py
from __future__ import annotations
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

    def map_error(self, func: Callable[..., object]) -> Success[A]:
        return self  # A Success has no error to transform

@dataclass(frozen=True)
class Failure[E]:
    error: E

    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Failure[E]:
        return self

    def map_error[F](self, func: Callable[[E], F]) -> Failure[F]:
        return Failure(func(self.error))

type Result[A, E] = Success[A] | Failure[E]

def prefix(msg: str) -> str:
    return f"error: {msg}"

print(Success(5).map_error(prefix))
#: Success(answer=5)
print(Failure("boom").map_error(prefix))
#: Failure(error='error: boom')
```

`map_error()` is `bind()`'s mirror image: `bind()` transforms the
success value and leaves a failure alone, while `map_error()`
transforms the failure value and leaves a success alone. `Success`'s
version is a no-op, since there is no error to touch. `Failure`'s
version applies `func` to `self.error` and wraps the result in a new
`Failure`. Adding a prefix to every error in a chain is then one call,
`result.map_error(prefix)`, applied once at the boundary where the
error is reported, rather than threading the prefix through every
function that might produce one.

## 3. `combined()` that collects every failure

```python
# test_ch14_combined.py
from __future__ import annotations
from dataclasses import dataclass

# Concrete (non-generic): this exercise combines three ints into
# a str, so there is no type parameter to preserve, and isinstance()
# can narrow a concrete class without running into type erasure.
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
    errors = [r.error for r in (result_a, result_b, result_c)
              if isinstance(r, ErrorResult)]
    if errors:
        return MultiErrorResult(errors)
    assert isinstance(result_a, IntResult)
    assert isinstance(result_b, IntResult)
    assert isinstance(result_c, IntResult)
    return add(result_a.value, result_b.value, result_c.value)

def test_combined_collects_every_failure() -> None:
    assert combined(1, 2) == MultiErrorResult(
        ["func_a(1)", "func_b(2)", "func_c(3): division by zero"])

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
list of error strings." Reusing one generic `Success[A]`/`Failure[E]`
pair for both would ask a type checker to recover a type parameter
from a plain `isinstance()` check, which Python's runtime type
erasure makes impossible in general; `ty` reports exactly that gap as
an error. Two small concrete classes sidestep the problem entirely,
since there is no parameter to lose.
