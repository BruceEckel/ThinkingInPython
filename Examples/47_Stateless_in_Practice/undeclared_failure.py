# undeclared_failure.py
from stateless import Success, catch, run, success

def ratio(a: int, b: int) -> Success[float]:
    return success(a / b)

def caller() -> Success[float | ZeroDivisionError]:
    out: float | ZeroDivisionError
    out = yield from catch(ZeroDivisionError)(ratio)(1, 0)
    return out

try:
    run(caller())
except ZeroDivisionError as e:
    print(type(e).__name__)
#: ZeroDivisionError
