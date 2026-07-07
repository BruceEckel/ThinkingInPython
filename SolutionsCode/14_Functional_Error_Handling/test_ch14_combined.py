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
