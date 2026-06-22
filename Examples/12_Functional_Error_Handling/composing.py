# composing.py
# Composing functions that return Results, by hand. Each step checks
# for a Failure and returns early. An exception can be turned into a
# Failure value instead of being raised.
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
