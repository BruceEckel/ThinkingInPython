# exercise_4.py
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Protocol, final

@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

@final
@dataclass(frozen=True)
class Err[E]:
    error: E

type Result[A, E] = Ok[A] | Err[E]

class SafeDecorator(Protocol):
    def __call__[**P, A](
        self, func: Callable[P, A]
    ) -> Callable[P, Result[A, Exception]]: ...

def safe(*catch: type[Exception]) -> SafeDecorator:
    def decorate[**P, A](
        func: Callable[P, A]
    ) -> Callable[P, Result[A, Exception]]:
        @wraps(func)
        def wrapper(
            *args: P.args, **kwargs: P.kwargs
        ) -> Result[A, Exception]:
            try:
                return Ok(func(*args, **kwargs))
            except catch as e:
                return Err(e)
        return wrapper
    return decorate

@safe(ValueError)
def parse(text: str) -> int:
    if not text.isdigit():
        raise TypeError(f"{text!r} is not digits")
    return int(text)

print(parse("42"))
#: Ok(answer=42)
try:
    parse("oops")
except TypeError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: TypeError: 'oops' is not digits
