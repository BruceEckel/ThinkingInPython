# lambda_decoration.py
from collections.abc import Callable

def loud(func: Callable[[int], int]) -> Callable[[int], int]:
    def wrapper(n: int) -> int:
        print(f"calling with {n}")
        return func(n)
    return wrapper

double = loud(lambda n: n * 2)

if __name__ == "__main__":
    print(double(21))
#: calling with 21
#: 42
