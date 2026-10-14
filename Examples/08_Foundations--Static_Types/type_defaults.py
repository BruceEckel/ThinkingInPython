# type_defaults.py
from typing import reveal_type

class Stack[T = str]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def top(self) -> T:
        return self.items[-1]

words: Stack = Stack()  # No brackets, so T is str
words.push("beta")
reveal_type(words.top())  # ty: str
print(words.top().upper())
#: BETA
counts: Stack[int] = Stack()
counts.push(2)
print(counts.top() + 1)
#: 3
