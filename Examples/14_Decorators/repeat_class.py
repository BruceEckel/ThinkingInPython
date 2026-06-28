# repeat_class.py
from collections.abc import Callable
from functools import wraps

class repeat:
    def __init__(self, times: int) -> None:
        self.times = times  # The decoration arguments

    def __call__[**P, R](
        self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            for _ in range(self.times - 1):
                result = func(*args, **kwargs)
            return result
        return wrapper

@repeat(times=3)
def greet(name: str) -> None:
    print(f"Hello, {name}")

if __name__ == "__main__":
    greet("Bob")
#: Hello, Bob
#: Hello, Bob
#: Hello, Bob
