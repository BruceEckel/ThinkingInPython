# type_defaults.py

class Stack[T = str]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def top(self) -> T:
        return self.items[-1]

words: Stack = Stack()  # No brackets, so T is str
words.push("beta")
print(words.top().upper())
#: BETA
counts: Stack[int] = Stack()
counts.push(2)
print(counts.top() + 1)
#: 3

type Pair[T = int] = tuple[T, T]

def is_origin(point: Pair) -> bool:  # Pair means Pair[int]
    return point == (0, 0)

print(is_origin((0, 0)))
#: True
