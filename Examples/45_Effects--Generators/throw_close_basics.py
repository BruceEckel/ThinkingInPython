# throw_close_basics.py
import inspect
from collections.abc import Generator
from exceptions import expect

def pause() -> Generator[None]:
    print("started")
    yield
    print("resumed")

g = pause()
next(g)
#: started
expect(ValueError, g.throw, ValueError("stop"))  # [1]
#: [ValueError] stop

g = pause()
next(g)
#: started
g.close()  # [2]
print(inspect.getgeneratorstate(g))
#: GEN_CLOSED
