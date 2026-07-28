# yield_to_exhaustion.py
from collections.abc import Generator

def inner(chars: str) -> Generator[str, int, str]:
    result = "| "
    for c in chars:
        result += f"{c.upper()} | "
        yield c
    return result

def outer(chars: str) -> Generator[str, int, str]:
    result = yield from inner(chars)
    return f"outer received [{result}]"

print(outer("abcdefg"))
#: <generator object outer at 0x0000015E4147D9A0>
