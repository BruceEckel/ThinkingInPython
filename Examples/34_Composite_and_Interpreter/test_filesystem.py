# test_filesystem.py
from typing import Final
import pytest
from filesystem import Directory, File, Node, disk_usage, walk

SUB: Final[Directory] = Directory(
    "sub", (File("b", 2), File("c", 3)))
TREE: Final[Directory] = Directory(
    "top", (File("a", 1), SUB))

@pytest.mark.parametrize("entry, expected", [
    (TREE, 6),
    (SUB, 5),
    (File("solo", 7), 7),
])
def test_disk_usage_is_uniform(entry: Node, expected: int) -> None:
    assert disk_usage(entry) == expected

def test_walk_yields_full_paths() -> None:
    assert list(walk(TREE)) == [
        "top/a", "top/sub/b", "top/sub/c"]

def test_empty_directory() -> None:
    assert disk_usage(Directory("empty", ())) == 0
    assert list(walk(Directory("empty", ()))) == []
