# type_defaults_bare.py
from typing import reveal_type

class BareStack[T]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def top(self) -> T:
        return self.items[-1]

pile: BareStack = BareStack()  # No brackets, T unsolved
pile.push("first")
reveal_type(pile.top())  # ty: Unknown
