# FunctionalErrorHandling/returning_result.py
# A function reports failure by returning Failure, success by returning Success.
# The return type now says exactly that: Result[int, str].
from result import Failure, Result, Success


def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)


if __name__ == "__main__":
    for i in range(3):
        print(i, func_a(i))
