# type_defaults_bare.py
from typing import reveal_type

class Queue[T]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def top(self) -> T:
        return self.items[-1]

line: Queue = Queue()  # No brackets, T unsolved
line.push("first")
reveal_type(line.top())  # ty: Unknown
