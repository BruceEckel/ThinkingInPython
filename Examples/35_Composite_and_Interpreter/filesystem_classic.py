# filesystem_classic.py
from abc import ABC, abstractmethod
from typing import override

class Node(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def size(self) -> int: ...

class File(Node):
    def __init__(self, name: str, byte_count: int) -> None:
        super().__init__(name)
        self.byte_count = byte_count

    @override
    def size(self) -> int:
        return self.byte_count

class Directory(Node):
    def __init__(self, name: str, *entries: Node) -> None:
        super().__init__(name)
        self.entries = entries

    @override
    def size(self) -> int:
        return sum(e.size() for e in self.entries)

src = Directory(
    "src", File("main.py", 400), File("util.py", 250))
root = Directory(
    "root", File("readme.md", 90), src, File("data.csv", 1200))
print(root.size(), src.size(), File("lone.txt", 10).size())
#: 1940 650 10
