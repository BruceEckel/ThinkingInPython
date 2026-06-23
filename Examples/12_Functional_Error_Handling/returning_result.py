# returning_result.py
from result import Failure, Result, Success

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)

if __name__ == "__main__":
    for i in range(5):
        print(i, func_a(i))
