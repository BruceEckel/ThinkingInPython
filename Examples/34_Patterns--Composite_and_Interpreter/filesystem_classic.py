# filesystem_classic.py
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import override

class Node(ABC):
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

    @abstractmethod
    def walk(self, prefix: str = "") -> Iterator[str]: ...

@dataclass(frozen=True)
class File(Node):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        return self.size

    @override
    def walk(self, prefix: str = "") -> Iterator[str]:
        yield prefix + self.name

@dataclass(frozen=True)
class Directory(Node):
    name: str
    entries: tuple[Node, ...]

    @override
    def disk_usage(self) -> int:
        return sum(e.disk_usage() for e in self.entries)

    @override
    def walk(self, prefix: str = "") -> Iterator[str]:
        for e in self.entries:
            yield from e.walk(f"{prefix}{self.name}/")

src = Directory("src", (
    File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, File("data.csv", 1200)))
print(root.disk_usage(), src.disk_usage(),
      File("lone.txt", 10).disk_usage())
#: 1940 650 10
for path in root.walk():
    print(path)
#: root/readme.md
#: root/src/main.py
#: root/src/util.py
#: root/data.csv
