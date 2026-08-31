# except_vs_catch.py
from typing import assert_never
from scores import score
from stateless import Success, Try, catch, run

def guarded(name: str) -> Try[KeyError, str]:
    try:
        value = yield from score(name)
    except KeyError:
        return f"{name}: unknown"
    return f"{name}: {value}"

def moved(name: str) -> Success[str]:
    value: int | KeyError = yield from (
        catch(KeyError)(score)(name))
    match value:
        case KeyError():
            return f"{name}: unknown"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

print(run(guarded("Carol")), run(moved("Carol")))
#: Carol: unknown Carol: unknown
print(repr(run(catch(KeyError)(guarded)("Carol"))))
#: KeyError('Carol')
