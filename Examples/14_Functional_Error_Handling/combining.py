# combining.py
from composing import func_b, func_c
from result import Result, Success
from returning_result import func_a

def add(a: int, b: int, c: int) -> str:
    return f"add({a} + {b} + {c}): {a + b + c}"

def combined(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: func_c(i + j).bind(
                lambda c: Success(add(a, b, c)))))

if __name__ == "__main__":
    for args in [(1, 5), (7, 2), (2, 1), (7, 5)]:
        print(args, combined(*args))
#: (1, 5) Failure(error='func_a(1)')
#: (7, 2) Failure(error='func_b(2)')
#: (2, 1) Failure(error='func_c(3): division by zero')
#: (7, 5) Success(answer='add(7 + 5 + 12): 24')
