# count_calls.py
from collections.abc import Callable
from functools import update_wrapper
from typing import Any


class count_calls:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.count = 0
        update_wrapper(self, func)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.count += 1
        print(f"call {self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)


@count_calls
def hello() -> None:
    print("hello")


if __name__ == "__main__":
    hello()
    hello()
    print(hello.count)  # 2: the state lives on the decorator instance
