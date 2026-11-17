# failure.py
from exceptions import expect
from stateless import run, throws

@throws(ZeroDivisionError)
def inverse(n: int) -> float:
    return 1 / n

print(run(inverse(4)))
#: 0.25
expect(ZeroDivisionError, run, inverse(0))
#: [ZeroDivisionError] division by zero
