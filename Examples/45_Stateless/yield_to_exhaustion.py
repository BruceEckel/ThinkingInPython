# yield_to_exhaustion.py
from collections.abc import Generator

def inner(chars: str) -> Generator[str, None, str]:
    result = "| "
    for c in chars:
        result += f"{c.upper()} | "
        yield c
    return result

def outer(chars: str) -> Generator[str, None, str]:
    result = yield from inner(chars)
    return f"outer received [{result}]"

def top(chars: str) -> Generator[str, None, str]:
    result = yield from outer(chars)
    result2 = yield from inner(chars)
    return f"top:\n[{result}]\n[{result2}]"

def run(g: Generator[str, None, str]) -> tuple[list[str], str]:
    yielded: list[str] = []
    while True:
        try:
            yielded.append(next(g))
        except StopIteration as stop:
            return yielded, stop.value

yields, returned = run(outer("abcd"))
print(yields)
#: ['a', 'b', 'c', 'd']
print(returned)
#: outer received [| A | B | C | D | ]
yields, returned = run(top("abcd"))
print(yields)
#: ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd']
print(returned)
#: top:
#: [outer received [| A | B | C | D | ]]
#: [| A | B | C | D | ]
