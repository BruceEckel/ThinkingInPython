# functools_wraps.py
from collections.abc import Callable
from functools import wraps

def trace(func: Callable[[str], str]) -> Callable[[str], str]:
    @wraps(func)
    def wrapper(name: str) -> str:
        return func(name)
    return wrapper

@trace
def greet(name: str) -> str:
    "Say hello."
    return f"Hello, {name}!"

print(greet.__name__, "-", greet.__doc__)
#: greet - Say hello.
