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
