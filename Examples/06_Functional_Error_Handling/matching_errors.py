# matching_errors.py
# Because the error is a value, often an exception, you can match the
# Result and the exception type together, and handle each kind.
from result import Failure, Result, Success
from safe import safe


@safe
def parse(text: str) -> int:
    return int(text)


@safe
def reciprocal(n: int) -> float:
    return 1 / n


def describe(text: str) -> str:
    result: Result[float, Exception] = parse(text).bind(reciprocal)
    match result:
        case Success(answer):
            return f"{text}: {answer}"
        case Failure(ValueError()):
            return f"{text}: not a number"
        case Failure(ZeroDivisionError()):
            return f"{text}: cannot divide by zero"
        case Failure(error):
            return f"{text}: {type(error).__name__}"


if __name__ == "__main__":
    for text in ("4", "0", "oops"):
        print(describe(text))
