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
