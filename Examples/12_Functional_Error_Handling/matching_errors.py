# matching_errors.py
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
            return f"{text}: Not a number"
        case Failure(ZeroDivisionError()):
            return f"{text}: Cannot divide by zero"
        case Failure(error):
            return f"{text}: {type(error).__name__}"

if __name__ == "__main__":
    for text in ("4", "0", "OOPS"):
        print(describe(text))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
