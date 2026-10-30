# throw_close_basics.py
from collections.abc import Generator
from exceptions import expect

def pause() -> Generator[str]:
    print("started")
    yield "paused"
    print("resumed")

g = pause()
print(next(g))
#: started
#: paused
expect(ValueError, g.throw, ValueError("stop"))
#: [ValueError] stop

g = pause()
next(g)
#: started
g.close()
print("closed")
#: closed
