# throw_close_basics.py
import inspect
from collections.abc import Generator
from exceptions import expect

def worker() -> Generator[str, None, str]:
    try:
        try:
            yield "ready"
            print("resumed")
        except ValueError as e:
            print(f"caught: {e}")
            yield "recovered"
        finally:
            print("cleanup")
    except GeneratorExit:
        return "closed"
    return "done"

g = worker()
print(next(g))
#: ready
print(g.throw(ValueError("bad input")))  # [1]
#: caught: bad input
#: recovered
print(g.close())  # [2]
#: cleanup
#: closed
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = worker()
print(next(g))
#: ready
expect(TypeError, g.throw, TypeError("stop"))  # [3]
#: cleanup
#: [TypeError] stop
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = worker()
print(next(g))
#: ready
expect(StopIteration, next, g)  # [4]
#: resumed
#: cleanup
#: [StopIteration] done
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
