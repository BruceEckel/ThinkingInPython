# safe.py
from collections.abc import Callable
from functools import wraps
from result import Failure, Result, Success

def safe[A](
    func: Callable[..., A],
) -> Callable[..., Result[A, Exception]]:
    @wraps(func)
    def wrapper(
        *args: object, **kwargs: object
    ) -> Result[A, Exception]:
        try:
            return Success(func(*args, **kwargs))
        except Exception as e:
            return Failure(e)
    return wrapper

@safe
def parse(text: str) -> int:
    return int(text)

if __name__ == "__main__":
    for text in ("42", "oops"):
        match parse(text):
            case Success(answer):
                print(f"{text}: parsed {answer}")
            case Failure(error):
                print(f"{text}: {type(error).__name__}")
#: 42: parsed 42
#: oops: ValueError
