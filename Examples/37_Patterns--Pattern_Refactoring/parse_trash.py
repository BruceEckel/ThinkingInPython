# parse_trash.py
from pathlib import Path
from trash import Trash

def parse(filename: str | Path) -> list[Trash]:
    items: list[Trash] = []
    for line in Path(filename).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, weight = line.split(":")
        items.append(
            Trash.create(name.strip(), float(weight)))
    return items
