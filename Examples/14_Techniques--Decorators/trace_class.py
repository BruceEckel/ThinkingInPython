# trace_class.py
from collections.abc import Callable
from functools import update_wrapper
from tracer import call_text

class trace[**P, R]:
    __name__: str  # Set by update_wrapper(), not __init__

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        # Copy __name__, __doc__, etc
        update_wrapper(self, func)

    def __call__(self, *args: P.args,
                 **kwargs: P.kwargs) -> R:
        print("->", call_text(self.__name__, args, kwargs))
        result = self.func(*args, **kwargs)
        print(f"<- {self.__name__} = {result!r}")
        return result

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, b=3)
#: -> add(2, b=3)
#: <- add = 5
