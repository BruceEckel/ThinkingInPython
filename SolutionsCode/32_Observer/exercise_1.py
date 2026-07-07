# exercise_1.py
from collections.abc import Callable
from functools import wraps
from typing import Any

def trace_all(cls: type) -> type:
    for name, value in vars(cls).copy().items():
        if callable(value) and not name.startswith("__"):
            def make_wrapper(
                func: Callable, name: str = name
            ) -> Callable:
                @wraps(func)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    print(f"-> {name}")
                    result = func(*args, **kwargs)
                    print(f"<- {name}")
                    return result
                return wrapper
            setattr(cls, name, make_wrapper(value))
    return cls

@trace_all
class Greeter:
    def hello(self, name: str) -> str:
        return f"Hello, {name}"

    def bye(self) -> str:
        return "Bye"

g = Greeter()
print(g.hello("Bob"))
#: -> hello
#: <- hello
#: Hello, Bob
