# throw_through.py
from collections.abc import Generator

def inner() -> Generator[str]:
    try:
        yield "inner ready"
    except ValueError as e:
        print(f"inner caught: {e}")
        yield "inner recovered"
    finally:
        print("inner cleanup")

def outer() -> Generator[str]:
    try:
        yield from inner()
    finally:
        print("outer cleanup")

g = outer()
print(next(g))
#: inner ready
print(g.throw(ValueError("bad input")))
#: inner caught: bad input
#: inner recovered
g.close()
#: inner cleanup
#: outer cleanup
