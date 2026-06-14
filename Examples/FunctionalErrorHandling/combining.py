# FunctionalErrorHandling/combining.py
# Combining several Results that come from different inputs. Nested binds carry
# each answer inward; a Failure anywhere short-circuits to the end.
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
