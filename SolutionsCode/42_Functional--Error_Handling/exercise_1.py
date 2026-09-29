# exercise_1.py
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
    print(f"func_c({i}) runs")
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        return Err(f"func_c({i}): {e}")
    return Ok(i)

def func_d(i: int) -> Result[int, str]:
    if i == 4:
        return Err(f"func_d({i})")
    return Ok(i)

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_d).bind(func_c)

for i in range(5):
    print(i, composed(i))
#: func_c(0) runs
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Err(error='func_b(2)')
#: func_c(3) runs
#: 3 Err(error='func_c(3): division by zero')
#: 4 Err(error='func_d(4)')
