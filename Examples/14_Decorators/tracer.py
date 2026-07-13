# tracer.py
from collections.abc import Callable
from functools import wraps

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        positional = [repr(a) for a in args]
        named = [f"{k}={v!r}" for k, v in kwargs.items()]
        arglist = ", ".join(positional + named)
        print(f"-> {func.__name__}({arglist})")  # type: ignore
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} = {result!r}")  # type: ignore
        return result
    return wrapper

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, b=3)
#: -> add(2, b=3)
#: <- add = 5
