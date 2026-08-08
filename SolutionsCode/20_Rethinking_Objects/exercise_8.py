# exercise_8.py
from dataclasses import dataclass, field
from typing import ClassVar, override

@dataclass
class Stack:
    items: list[int] = field(default_factory=list)

    def push(self, item: int) -> None:
        self.items.append(item)

@dataclass
class BoundedStack(Stack):
    limit: ClassVar[int] = 2

    def full(self) -> bool:  # The limit, exposed as a question
        return len(self.items) >= self.limit

    @override
    def push(self, item: int) -> None:  # Always succeeds
        super().push(item)
        del self.items[:-self.limit]  # Drop the oldest

def fill(stack: Stack, count: int) -> int:
    for n in range(count):
        stack.push(n)
    return len(stack.items)

print(fill(Stack(), 5))
#: 5
print(fill(BoundedStack(), 5))  # No exception now
#: 2

bounded = BoundedStack()
bounded.push(1)
print(bounded.full())
#: False
bounded.push(2)
print(bounded.full(), bounded.items)
#: True [1, 2]
