# matching_errors.py
from result import Err, Ok, Result
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

@safe
def reciprocal(n: int) -> float:
    return 1 / n

def compute(text: str) -> Result[float, Exception]:
    return parse(text).bind(reciprocal)

def describe(result: Result[float, Exception]) -> str:
    match result:
        case Ok(answer):
            return str(answer)
        case Err(ValueError()):
            return "Not a number"
        case Err(ZeroDivisionError()):
            return "Cannot divide by zero"
        case Err(error):
            return type(error).__name__

if __name__ == "__main__":
    results = {text: compute(text)
               for text in ("4", "0", "OOPS")}
    for text, result in results.items():
        print(f"{text}: {describe(result)}")
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
