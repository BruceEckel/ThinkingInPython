# exercise_10.py
import inspect
from collections.abc import Generator, Iterator
from enum import StrEnum
from types import GeneratorType
from typing import override

class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

type Name = str
type Path = str
type Tree = dict[Name, Tree | Color]
type Item = tuple[Name, Tree | Color]
type Level = tuple[Path, Iterator[Item]]

def visit(tree: Tree, at: Path = "") -> Generator[str]:
    for name, node in tree.items():
        if isinstance(node, dict):
            yield from visit(node, f"{at}{name}/")
        else:
            yield f"{at}{name}: {node}"

def level(tree: Tree, at: Path = "") -> Level:
    return at, iter(tree.items())

class Paths(Iterator[str]):
    def __init__(self, tree: Tree) -> None:
        self.stack: list[Level] = [level(tree)]

    @override
    def __next__(self) -> str:
        while self.stack:
            at, items = self.stack[-1]
            match next(items, None):
                case None:
                    self.stack.pop()  # [1]
                case name, dict() as subtree:
                    self.stack.append(  # [2]
                        level(subtree, f"{at}{name}/"))
                case name, color:
                    return f"{at}{name}: {color}"  # [3]
        raise StopIteration

def prefixes(walk: Iterator[str] | None) -> list[Path]:
    found: list[Path] = []
    while isinstance(walk, GeneratorType):
        found.append(inspect.getgeneratorlocals(walk)["at"])
        walk = walk.gi_yieldfrom
    return found

garden: Tree = {
    "rose": Color.RED,
    "beds": {
        "fern": Color.GREEN,
        "tulip": Color.RED,
        "pond": {"iris": Color.BLUE, "reed": Color.GREEN},
    },
    "ivy": Color.GREEN,
}
print(list(Paths(garden)) == list(visit(garden)))
#: True
print(list(Paths({"bed": {}, "ivy": Color.GREEN})))
#: ['ivy: green']
paths = Paths(garden)
print([next(paths) for _ in range(4)][-1])
#: beds/pond/iris: blue
print([at for at, _ in paths.stack])
#: ['', 'beds/', 'beds/pond/']
walk = visit(garden)
print([next(walk) for _ in range(4)][-1])
#: beds/pond/iris: blue
print(prefixes(walk))
#: ['', 'beds/', 'beds/pond/']
