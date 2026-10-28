# filesystem.py
from collections.abc import Iterator
from typing import assert_never
from record import record

@record
class File:
    name: str
    size: int

@record
class Directory:
    name: str
    entries: tuple[Node, ...]

type Node = File | Directory
type Location = str

def disk_usage(entry: Node) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(child)
                       for child in entries)
        case _:
            assert_never(entry)

def walk(
    entry: Node, prefix: Location = ""
) -> Iterator[Location]:
    match entry:
        case File(name, _):
            yield prefix + name
        case Directory(name, entries):
            for child in entries:
                yield from walk(child, f"{prefix}{name}/")
        case _:
            assert_never(entry)
