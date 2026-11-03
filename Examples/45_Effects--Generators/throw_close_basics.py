# throw_close_basics.py
import inspect
from collections.abc import Generator
from exceptions import expect

def worker() -> Generator[str]:
    try:
        yield "ready"
        print("resumed")
    except ValueError as e:
        print(f"caught: {e}")
        yield "recovered"
    finally:
        print("cleanup")

g = worker()
print(next(g))
#: ready
print(g.throw(ValueError("bad input")))  # [1]
#: caught: bad input
#: recovered
g.close()  # [2]
#: cleanup
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = worker()
next(g)
expect(TypeError, g.throw, TypeError("stop"))  # [3]
#: cleanup
#: [TypeError] stop
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
