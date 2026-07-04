# test_filesystem.py
from typing import Final
from filesystem import Directory, File, disk_usage, walk

SUB: Final[Directory] = Directory(
    "sub", (File("b", 2), File("c", 3)))
TREE: Final[Directory] = Directory(
    "top", (File("a", 1), SUB))

def test_disk_usage_is_uniform() -> None:
    assert disk_usage(TREE) == 6
    assert disk_usage(SUB) == 5
    assert disk_usage(File("solo", 7)) == 7

def test_walk_yields_full_paths() -> None:
    assert list(walk(TREE)) == [
        "top/a", "top/sub/b", "top/sub/c"]

def test_empty_directory() -> None:
    assert disk_usage(Directory("empty", ())) == 0
    assert list(walk(Directory("empty", ()))) == []
