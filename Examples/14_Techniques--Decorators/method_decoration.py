# method_decoration.py
from collections.abc import Callable
from exceptions import expect

class logged:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __call__(self, *args: object,
                 **kwargs: object) -> object:
        return self.func(*args, **kwargs)

class Ex:
    @logged
    def method(self, x: int) -> int:
        return x

ex = Ex()
expect(TypeError, ex.method, 5)
#: [TypeError] Ex.method() missing 1 required positional
#: argument: 'x'
