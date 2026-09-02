# test_ch42_combined.py
from dataclasses import dataclass
from typing import final

# The chapter's Result, reduced to what this answer uses:
# the generic pair and the alias, without bind().
@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

@final
@dataclass(frozen=True)
class Err[E]:
    error: E

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
