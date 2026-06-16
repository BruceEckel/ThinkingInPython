# repeat_class.py
from collections.abc import Callable
from functools import wraps
from typing import Any


class repeat:
    def __init__(self, times: int) -> None:
        self.times = times  # the decoration arguments

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            for _ in range(self.times):
                result = func(*args, **kwargs)
            return result
        return wrapper


@repeat(times=3)
def greet(name: str) -> None:
    print(f"Hello, {name}")


if __name__ == "__main__":
    greet("Bob")
