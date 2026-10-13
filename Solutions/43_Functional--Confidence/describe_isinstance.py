# describe_isinstance.py
from typing import final
from record import record

@final
@record
class Ok[A]:
    answer: A

@final
@record
class Err[E]:
    error: E

type Result[A, E] = Ok[A] | Err[E]

def compute(text: str) -> Result[float, Exception]:
    try:
        return Ok(1 / int(text))
    except (ValueError, ZeroDivisionError) as e:
        return Err(e)

def describe(result: Result[float, Exception]) -> str:
    if isinstance(result, Ok):
        return str(result.answer)
    if isinstance(result.error, ValueError):
        return "Not a number"
    if isinstance(result.error, ZeroDivisionError):
        return "Cannot divide by zero"
    return type(result.error).__name__  # [1]

for sample in ("4", "0", "OOPS"):
    print(f"{sample}: {describe(compute(sample))}")
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
