# trace_class.py
from collections.abc import Callable
from functools import update_wrapper

class trace[**P, R]:
    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        update_wrapper(self, func)  # Copy __name__, __doc__, etc

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        arglist = ", ".join(repr(a) for a in args)
        print(f"-> {self.func.__name__}({arglist})")  # type: ignore
        result = self.func(*args, **kwargs)
        print(f"<- {self.func.__name__} = {result!r}")  # type: ignore
        return result

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, 3)
#: -> add(2, 3)
#: <- add = 5
