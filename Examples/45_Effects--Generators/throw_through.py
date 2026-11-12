# throw_through.py
from collections.abc import Generator

def innermost() -> Generator[str]:
    try:
        yield "innermost ready"
    except ValueError as e:
        print(f"innermost caught: {e}")
        yield "innermost recovered"
    finally:
        print("innermost cleanup")

def outer() -> Generator[str]:
    try:
        yield from innermost()
    finally:
        print("outer cleanup")

g = outer()
print(next(g))
#: innermost ready
print(g.throw(ValueError("bad input")))
#: innermost caught: bad input
#: innermost recovered
g.close()
#: innermost cleanup
#: outer cleanup
