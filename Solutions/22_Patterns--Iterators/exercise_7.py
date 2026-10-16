# exercise_7.py
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import count
from typing import Protocol

DONE = sentinel("DONE")

class GoFIterator[T](Protocol):
    def first(self) -> None: ...
    def advance(self) -> None: ...
    def is_done(self) -> bool: ...
    def current_item(self) -> T: ...

@dataclass
class OverSequence[T]:
    items: Sequence[T]
    index: int = 0

    def first(self) -> None:
        self.index = 0

    def advance(self) -> None:
        self.index += 1

    def is_done(self) -> bool:
        return self.index >= len(self.items)

    def current_item(self) -> T:
        return self.items[self.index]

class OverStream[T]:
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self.seen: list[T] = []
        self.index = 0

    def first(self) -> None:
        self.index = 0

    def advance(self) -> None:
        self.index += 1

    def is_done(self) -> bool:
        while len(self.seen) <= self.index:
            item = next(self.source, DONE)
            if item is DONE:
                return True
            self.seen.append(item)
        return False

    def current_item(self) -> T:
        return self.seen[self.index]

def traverse(it: GoFIterator[int]) -> list[int]:
    out: list[int] = []
    while not it.is_done():
        out.append(it.current_item())
        it.advance()
    return out

seq = OverSequence([2, 4, 6])
print(traverse(seq))
#: [2, 4, 6]
seq.first()
print(traverse(seq))
#: [2, 4, 6]

endless = OverStream(count(1))
for _ in range(50_000):
    endless.is_done()
    endless.current_item()
    endless.advance()
print(len(endless.seen))
#: 50000
