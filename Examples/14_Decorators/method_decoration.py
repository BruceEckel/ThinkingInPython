# method_decoration.py
from collections.abc import Callable

class Logged:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, *args: object, **kwargs: object) -> object:
        return self.func(*args, **kwargs)

class Example:
    @Logged
    def method(self, x: int) -> int:
        return x

example = Example()
try:
    example.method(5)
except TypeError as e:
    print(e)
#: Example.method() missing 1 required positional argument: 'x'
