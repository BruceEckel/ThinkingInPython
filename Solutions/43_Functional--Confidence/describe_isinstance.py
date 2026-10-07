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

def describe(
    text: str, result: Result[float, Exception]
) -> str:
    if isinstance(result, Ok):
        return f"{text}: {result.answer}"
    if isinstance(result.error, ValueError):
        return f"{text}: Not a number"
    if isinstance(result.error, ZeroDivisionError):
        return f"{text}: Cannot divide by zero"
    return f"{text}: {type(result.error).__name__}"  # [1]

for sample in ("4", "0", "OOPS"):
    print(describe(sample, compute(sample)))
#: 4: 0.25
#: 0: Cannot divide by zero
#: OOPS: Not a number
