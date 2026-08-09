# exercise_9.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

class Entry(ABC):
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

@dataclass(frozen=True)
class File(Entry):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        return self.size

@dataclass(frozen=True)
class Directory(Entry):
    name: str
    entries: tuple[Entry, ...]

    @override
    def disk_usage(self) -> int:
        return sum(e.disk_usage() for e in self.entries)

# A plugin package adds a node type, editing nothing above:
@dataclass(frozen=True)
class Symlink(Entry):
    name: str
    target: str

    @override
    def disk_usage(self) -> int:
        return 0

src = Directory("src", (File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, Symlink("latest", "src")))
print(root.disk_usage())
#: 740
