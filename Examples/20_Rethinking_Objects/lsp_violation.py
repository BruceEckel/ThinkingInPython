# lsp_violation.py
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

    @override
    def push(self, item: int) -> None:
        if len(self.items) >= self.limit:
            raise OverflowError("Stack is full")
        super().push(item)

def fill(stack: Stack, count: int) -> int:
    for n in range(count):
        stack.push(n)
    return len(stack.items)

print(fill(Stack(), 5))
#: 5
try:
    fill(BoundedStack(), 5)
except OverflowError as e:
    print(type(e).__name__)
#: OverflowError
