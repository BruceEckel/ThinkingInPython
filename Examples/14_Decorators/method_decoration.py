# method_decoration.py
from collections.abc import Callable

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
try:
    ex.method(5)
except TypeError as e:
    print(e)
#: Ex.method() missing 1 required positional argument: 'x'
