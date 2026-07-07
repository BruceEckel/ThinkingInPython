# exercise_1.py
from collections.abc import Iterator
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class File:
    name: str
    size: int

@dataclass(frozen=True)
class Directory:
    name: str
    entries: tuple[Node, ...]

type Node = File | Directory

def find(entry: Node, name: str, prefix: str = "") -> Iterator[str]:
    match entry:
        case File(n, _):
            if n == name:
                yield prefix + n
        case Directory(n, entries):
            if n == name:
                yield prefix + n
            for e in entries:
                yield from find(e, name, f"{prefix}{n}/")
        case _:
            assert_never(entry)

src = Directory("src", (File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, File("data.csv", 1200),
    Directory("src", ())))

print(list(find(root, "main.py")))
#: ['root/src/main.py']
print(list(find(root, "src")))
#: ['root/src', 'root/src']
