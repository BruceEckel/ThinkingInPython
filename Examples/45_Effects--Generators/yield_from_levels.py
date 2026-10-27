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

def report() -> Iterator[Yielded | Returned]:
    yield (yield from outer())

for yielded in report():
    print(yielded)
#: Yielded(text='outer')
#: Yielded(text='middle')
#: Yielded(text='inner')
#: Returned(text='Message from inner!')
