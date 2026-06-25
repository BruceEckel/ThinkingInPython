# count_calls.py
from collections.abc import Callable
from functools import update_wrapper

class count_calls[**P, R]:
    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        self.count = 0
        update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        self.count += 1
        print(f"call {self.count} of {self.func.__name__}")  # type: ignore
        return self.func(*args, **kwargs)

@count_calls
def hello() -> None:
    print("hello")

if __name__ == "__main__":
    hello()
    hello()
    print(hello.count)  # The state lives on the decorator instance
## call 1 of hello
## hello
## call 2 of hello
## hello
## 2
