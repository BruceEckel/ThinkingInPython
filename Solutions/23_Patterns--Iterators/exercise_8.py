# exercise_8.py
from collections.abc import Iterable, Iterator
from typing import override

DONE = sentinel("DONE")

class Peekable[T](Iterator[T]):
    def __init__(self, source: Iterable[T]) -> None:
        self.source: Iterator[T] = iter(source)
        self.stored: T | DONE = next(self.source, DONE)

    def peek(self) -> T | DONE:
        return self.stored  # Reports without consuming

    @override
    def __next__(self) -> T:
        if self.stored is DONE:
            raise StopIteration
        item = self.stored
        self.stored = next(self.source, DONE)
        return item

it = Peekable(x * 2 for x in [1, 2, 3])
# Free, and repeatable
print(it.peek(), it.peek(), it.peek())
#: 2 2 2
print(next(it))
#: 2
print(it.peek())
#: 4
print(list(it))  # Still an ordinary iterator
#: [4, 6]
print(it.peek() is DONE)
#: True
