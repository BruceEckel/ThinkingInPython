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

def describe(
    text: str, result: Result[float, Exception]
) -> str:
    match result:
        case Ok(answer):
            return f"{text}: {answer}"
        case Err(ValueError()):
            return f"{text}: Not a number"
        case Err(ZeroDivisionError()):
            return f"{text}: Cannot divide by zero"
        case Err(error):
            return f"{text}: {type(error).__name__}"

if __name__ == "__main__":
    texts = ("4", "0", "OOPS")
    # Every Result computed first, matched after:
    results = [compute(text) for text in texts]
    for text, result in zip(texts, results):
        print(describe(text, result))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
