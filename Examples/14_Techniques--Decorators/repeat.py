# repeat.py
from collections.abc import Callable
from functools import wraps

def repeat[**P, R](
        times: int
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if times < 1:
        raise ValueError(f"times must be >= 1, got {times}")
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(times):
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
#: Hello, Bob
#: Hello, Bob
#: Hello, Bob
