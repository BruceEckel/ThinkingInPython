# composing.py
from result import Err, Ok, Result
from returning_result import func_a

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Err(f"func_b({i})")
    return Ok(i)

def func_c(i: int) -> Result[int, str]:
    try:
        1 / (i - 3)  # A probe: raises an exception when i == 3
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
