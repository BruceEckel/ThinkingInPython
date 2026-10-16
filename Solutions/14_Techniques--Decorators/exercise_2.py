# exercise_2.py
import time
from collections.abc import Callable, Mapping
from functools import wraps

def call_text(name: str, args: tuple[object, ...],
              kwargs: Mapping[str, object]) -> str:
    positional = [repr(a) for a in args]
    named = [f"{k}={v!r}" for k, v in kwargs.items()]
    return f"{name}({', '.join(positional + named)})"

def trace[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        name = wrapper.__name__
        print("->", call_text(name, args, kwargs))
        result = func(*args, **kwargs)
        print(f"<- {name} = {result!r}")
        return result
    return wrapper

def timing[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        ok = elapsed >= 0
        name = wrapper.__name__
        print(f"{name} timed, non-negative: {ok}")
        return result
    return wrapper

@trace
@timing
def add(a: int, b: int) -> int:
    return a + b

add(2, 3)
#: -> add(2, 3)
#: add timed, non-negative: True
#: <- add = 5
