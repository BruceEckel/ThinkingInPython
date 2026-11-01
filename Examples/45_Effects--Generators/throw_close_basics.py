# throw_close_basics.py
import inspect
from collections.abc import Generator
from exceptions import expect

def pause() -> Generator[None]:
    try:
        yield
        print("resumed")
    finally:
        print("finished")

g = pause()
next(g)
expect(ValueError, g.throw, ValueError("stop"))  # [1]
#: finished
#: [ValueError] stop
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED

g = pause()
next(g)
g.close()  # [2]
#: finished
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
