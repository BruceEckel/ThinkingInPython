# exercise_3.py
from typing import Final, assert_never, reveal_type
from stateless import Success, Try, catch, throws

RAW: Final[dict[str, str]] = {"Alice": "42", "Bob": "seven"}

@throws(KeyError, ValueError)
def read_score(name: str) -> int:
    text = RAW[name]  # KeyError
    return int(text)  # ValueError

both = catch(KeyError, ValueError)(read_score)
one = catch(KeyError)(read_score)

def all_handled(name: str) -> Success[str]:
    value: int | KeyError | ValueError = yield from both(
        name)
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

if __name__ == "__main__":
    reveal_type(catch(ValueError)(one_unhandled))
