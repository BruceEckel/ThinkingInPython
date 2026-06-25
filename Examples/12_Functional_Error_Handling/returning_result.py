# returning_result.py
from result import Failure, Result, Success

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)

if __name__ == "__main__":
    for i in range(5):
        print(i, func_a(i))
## 0 Success(answer=0)
## 1 Failure(error='func_a(1)')
## 2 Success(answer=2)
## 3 Success(answer=3)
## 4 Success(answer=4)
