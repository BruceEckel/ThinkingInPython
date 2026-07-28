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
    result += yield from inner(chars[1:-1])
    return f"outer: [{result}]"

def top(chars: str) -> Generator[str, None, str]:
    result = yield from outer(chars)
    return f"top: [{result}]]"

def run(g: Generator[str, None, str]) -> tuple[list[str], str]:
    yielded: list[str] = []
    while True:
        try:
            yielded.append(next(g))
        except StopIteration as stop:
            return yielded, stop.value

yields, returned = run(outer("abcd"))
print(yields)
#: ['a', 'b', 'c', 'd', 'b', 'c']
print(returned)
#: outer received [| A | B | C | D | | B | C | ]
yields, returned = run(top("abcd"))
print(yields)
#: ['a', 'b', 'c', 'd', 'b', 'c', 'a', 'b', 'c', 'd']
print(returned)
#: top:
#: [outer received [| A | B | C | D | | B | C | ]]
#: [| A | B | C | D | ]
