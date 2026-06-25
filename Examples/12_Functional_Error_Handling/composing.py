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
## 0 Success(answer=0)
## 1 Failure(error='func_a(1)')
## 2 Failure(error='func_b(2)')
## 3 Failure(error='func_c(3): division by zero')
## 4 Success(answer=4)
