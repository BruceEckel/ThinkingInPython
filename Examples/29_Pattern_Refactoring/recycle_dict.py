# recycle_dict.py
# The Pythonic sort: the object's own type is the key. No type is
# named here, so this code never changes when you add a new kind of
# Trash.
from collections import defaultdict

from parse_trash import parse
from trash import Trash, sum_value


def main() -> None:
    bins: dict[type, list[Trash]] = defaultdict(list)
    for t in parse("trash.dat"):
        bins[type(t)].append(t)  # bin chosen by the piece itself
    for kind, items in bins.items():
        print(f"--- {kind.__name__} ---")
        sum_value(items)


if __name__ == "__main__":
    main()
