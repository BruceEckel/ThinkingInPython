# trace_descriptor.py
from collections.abc import Callable
from dataclasses import dataclass
from functools import update_wrapper
from types import MethodType

class trace[**P, R]:
    __name__: str  # Set by update_wrapper(), not __init__

    def __init__(self, func: Callable[P, R]) -> None:
        self.func = func
        update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        positional = [repr(a) for a in args]
        named = [f"{k}={v!r}" for k, v in kwargs.items()]
        arglist = ", ".join(positional + named)
        print(f"-> {self.__name__}({arglist})")
        result = self.func(*args, **kwargs)
        print(f"<- {self.__name__} = {result!r}")
        return result

    def __get__(
            self, obj: object, owner: type | None = None
    ) -> Callable[..., R]:
        if obj is None:
            return self  # Through the class, so nothing to bind
        return MethodType(self, obj)

@dataclass
class Greeter:
    name: str

    @trace
    def greet(self, greeting: str) -> str:
        return f"{greeting}, {self.name}"

print(Greeter("Bob").greet("Hello"))
#: -> greet(Greeter(name='Bob'), 'Hello')
#: <- greet = 'Hello, Bob'
#: Hello, Bob
