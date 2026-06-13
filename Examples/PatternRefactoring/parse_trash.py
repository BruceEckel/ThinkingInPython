# PatternRefactoring/parse_trash.py
# Read "Name:weight" lines into Trash objects through the registry.
from trash import Trash


def parse(filename: str) -> list[Trash]:
    items: list[Trash] = []
    with open(filename) as source:
        for line in source:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, weight = line.split(":")
            items.append(Trash.create(name.strip(), float(weight)))
    return items
