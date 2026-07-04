# filesystem.py
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
    entries: tuple[Entry, ...]

type Entry = File | Directory

def disk_usage(entry: Entry) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(e) for e in entries)
        case _:
            assert_never(entry)

def walk(entry: Entry, prefix: str = "") -> Iterator[str]:
    match entry:
        case File(name, _):
            yield prefix + name
        case Directory(name, entries):
            for e in entries:
                yield from walk(e, f"{prefix}{name}/")
        case _:
            assert_never(entry)

if __name__ == "__main__":
    src = Directory("src", (
        File("main.py", 400), File("util.py", 250)))
    root = Directory("root", (
        File("readme.md", 90), src, File("data.csv", 1200)))
    print(disk_usage(root), disk_usage(src),
          disk_usage(File("lone.txt", 10)))
    for path in walk(root):
        print(path)
#: 1940 650 10
#: root/readme.md
#: root/src/main.py
#: root/src/util.py
#: root/data.csv
