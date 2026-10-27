# yield_from_levels.py
from collections.abc import Generator, Iterator
from record import record

@record
class Yielded:
    text: str

@record
class Returned:
    text: str

def inner() -> Generator[Yielded, None, Returned]:
    yield Yielded("inner")
    return Returned("Message from inner!")

def middle() -> Generator[Yielded, None, Returned]:
    yield Yielded("middle")
    return (yield from inner())

def outer() -> Generator[Yielded, None, Returned]:
    yield Yielded("outer")
    return (yield from middle())

def report() -> Iterator[Yielded]:
    result: Returned = yield from outer()
    yield Yielded(f"returned: {result.text}")

for yielded in report():
    print(yielded)
#: Yielded(text='outer')
#: Yielded(text='middle')
#: Yielded(text='inner')
#: Yielded(text='returned: Message from inner!')
