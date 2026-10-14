# tracer.py
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

@trace
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    add(2, b=3)
#: -> add(2, b=3)
#: <- add = 5
