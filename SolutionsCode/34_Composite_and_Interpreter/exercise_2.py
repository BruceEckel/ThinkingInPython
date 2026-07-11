# exercise_2.py
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

@dataclass(frozen=True)
class Symlink:
    name: str
    target: str

type Node = File | Directory | Symlink

def disk_usage(entry: Node) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(e) for e in entries)
        case Symlink():
            return 0  # A link contributes no size of its own
        case _:
            assert_never(entry)

def walk(entry: Node, prefix: str = "") -> Iterator[str]:
    match entry:
        case File(name, _):
            yield prefix + name
        case Directory(name, entries):
            for e in entries:
                yield from walk(e, f"{prefix}{name}/")
        case Symlink(name, target):
            yield f"{prefix}{name} -> {target}"
        case _:
            assert_never(entry)

tree = Directory("root", (
    File("a.txt", 5), Symlink("shortcut", "/root/a.txt")))
print(disk_usage(tree))
#: 5
print(list(walk(tree)))
#: ['root/a.txt', 'root/shortcut -> /root/a.txt']
