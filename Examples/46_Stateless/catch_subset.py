# catch_subset.py
from typing import assert_never
from read_score import read_score
from stateless import Success, Try, catch, run

both = catch(KeyError, ValueError)(read_score)
one = catch(KeyError)(read_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from both(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case ValueError():
            return f"{name}: unreadable"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

def one_unhandled(name: str) -> Try[ValueError, str]:
    value: int | KeyError = yield from one(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

for who in ["Alice", "Bob", "Carol"]:
    print(run(all_handled(who)))
#: Alice: 42
#: Bob: unreadable
#: Carol: unknown
print(run(one_unhandled("Alice")))
#: Alice: 42
try:
    run(one_unhandled("Bob"))
except ValueError as e:
    print(type(e).__name__)
#: ValueError
