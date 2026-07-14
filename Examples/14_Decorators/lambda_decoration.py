# lambda_decoration.py
from collections.abc import Callable

def report(func: Callable[[int], int]) -> Callable[[int], int]:
    def wrapper(n: int) -> int:
        print(f"Calling {func.__name__} with {n}")  # type: ignore
        return func(n)
    return wrapper

double = report(lambda n: n * 2)

@report
def triple(n: int) -> int:
    return n * 3

if __name__ == "__main__":
    print(double(21))
    print(triple(21))
#: Calling <lambda> with 21
#: 42
#: Calling triple with 21
#: 63
