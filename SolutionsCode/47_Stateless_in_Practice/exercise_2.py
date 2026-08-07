# exercise_2.py
from typing import Final
from stateless import Success, catch, run, success, throws

RAW: Final[dict[str, int]] = {"Alice": 42}

def size(name: str) -> Success[int]:
    return success(RAW[name])  # KeyError, undeclared

def caller() -> Success[int | KeyError]:
    out: int | KeyError = yield from catch(KeyError)(size)("Bob")
    return out

try:
    run(caller())
except KeyError as e:
    print(f"escaped: {type(e).__name__}: {e}")
#: escaped: KeyError: 'Bob'

@throws(KeyError)
def declared_size(name: str) -> int:
    return RAW[name]

def fixed() -> Success[int | KeyError]:
    caught = catch(KeyError)(declared_size)
    out: int | KeyError = yield from caught("Bob")
    return out

print(type(run(fixed())).__name__)
#: KeyError
