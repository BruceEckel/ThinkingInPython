# color_count.py
from collections import Counter
from collections.abc import Generator, Iterator
from enum import StrEnum

class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

type Name = str
type Path = str
type Tree = dict[Name, Tree | Color]

def visit(
    tree: Tree, at: Path = ""
) -> Generator[str, None, Counter[Color]]:
    counts = Counter[Color]()
    for name, node in tree.items():
        if isinstance(node, dict):  # node is a Tree
            counts += yield from visit(node, f"{at}{name}/")
        else:  # node is a Color
            yield f"{at}{name}: {node}"
            counts[node] += 1
    return counts

def census(tree: Tree) -> Iterator[str]:
    counts: Counter = yield from visit(tree)
    for color, n in counts.items():
        yield f"{n} {color}"

garden: Tree = {
    "rose": Color.RED,
    "beds": {
        "fern": Color.GREEN,
        "tulip": Color.RED,
        "pond": {"iris": Color.BLUE, "reed": Color.GREEN},
    },
    "ivy": Color.GREEN,
}
for line in census(garden):
    print(line)
#: rose: red
#: beds/fern: green
#: beds/tulip: red
#: beds/pond/iris: blue
#: beds/pond/reed: green
#: ivy: green
#: 2 red
#: 3 green
#: 1 blue
