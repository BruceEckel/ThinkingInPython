# repeat.py
from collections.abc import Callable
from functools import wraps

def repeat[**P, R](
        times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            for _ in range(times - 1):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorate

@repeat(times=3)
def greet(name: str) -> str:
    print(f"Hello, {name}")
    return name

if __name__ == "__main__":
    greet("Bob")
## Hello, Bob
## Hello, Bob
## Hello, Bob
