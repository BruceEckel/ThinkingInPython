# recycle_rtti.py
# First cut: sort by testing each type. It works, but it checks for EVERY
# type. Add a new kind of Trash and you must find and edit this code, with
# no help from the tools if you miss a spot. That is the smell to watch for.
from collections import defaultdict

from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Paper, Trash, sum_value


def main() -> None:
    bins: dict[type, list[Trash]] = defaultdict(list)
    for t in parse("Trash.dat"):
        if isinstance(t, Aluminum):
            bins[Aluminum].append(t)
        elif isinstance(t, Paper):
            bins[Paper].append(t)
        elif isinstance(t, Glass):
            bins[Glass].append(t)
        elif isinstance(t, Cardboard):
            bins[Cardboard].append(t)
    for kind, items in bins.items():
        print(f"--- {kind.__name__} ---")
        sum_value(items)


if __name__ == "__main__":
    main()
