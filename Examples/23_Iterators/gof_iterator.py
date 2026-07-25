# gof_iterator.py
from collections.abc import Iterable, Iterator
from typing import Protocol

DONE = sentinel("DONE")

class GoFIterator[T](Protocol):
    def first(self) -> None: ...
    def advance(self) -> None: ...
    def is_done(self) -> bool: ...
    def current_item(self) -> T: ...

class OverStream[T]:
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self.lookahead: T | DONE = DONE
        self.advance()  # Pulled early, to answer is_done()

    def first(self) -> None:
        raise NotImplementedError("a stream cannot rewind")

    def advance(self) -> None:
        self.lookahead = next(self.source, DONE)

    def is_done(self) -> bool:
        return self.lookahead is DONE

    def current_item(self) -> T:
        if self.lookahead is DONE:
            raise IndexError("past the end")
        return self.lookahead

def walk(it: GoFIterator[int]) -> list[int]:
    out: list[int] = []
    while not it.is_done():
        out.append(it.current_item())
        it.advance()
    return out

stream = OverStream(x * 2 for x in [1, 2, 3])
print(walk(stream))
#: [2, 4, 6]
try:
    stream.first()
except NotImplementedError as e:
    print(e)
#: a stream cannot rewind
