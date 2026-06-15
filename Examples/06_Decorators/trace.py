# trace.py
from collections.abc import Callable
from functools import wraps


def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"-> {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} = {result!r}")
        return result
    return wrapper


@trace
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    add(2, 3)
