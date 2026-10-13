# functools_wraps.py
from collections.abc import Callable
from functools import wraps

type StrFn = Callable[[str], str]

def passthrough(func: StrFn) -> StrFn:
    @wraps(func)
    def wrapper(name: str) -> str:
        return func(name)
    return wrapper

def bare(func: StrFn) -> StrFn:
    def wrapper(name: str) -> str:
        return func(name)
    return wrapper

@passthrough
def greet(name: str) -> str:
    "Say hello."
    return f"Hello, {name}!"

@bare
def greet_bare(name: str) -> str:
    "Say hello."
    return f"Hello, {name}!"

print(greet.__name__, "-", greet.__doc__)
#: greet - Say hello.
print(greet_bare.__name__, "-", greet_bare.__doc__)
#: wrapper - None
