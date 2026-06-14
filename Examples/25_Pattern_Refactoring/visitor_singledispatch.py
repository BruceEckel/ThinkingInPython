# visitor_singledispatch.py
# Visitor's goal is to add operations to a fixed hierarchy from outside it.
# functools.singledispatch does that directly: a polymorphic function whose
# behavior is registered per type. Trash is never touched, new operations are
# independent functions, and new types just register themselves.
from functools import singledispatch

from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Trash


@singledispatch
def recycling_note(t: Trash) -> str:
    return f"{type(t).__name__}: no special handling"


@recycling_note.register
def _(t: Aluminum) -> str:
    return "Aluminum: crush and bale"


@recycling_note.register
def _(t: Glass) -> str:
    return "Glass: sort by color, then crush"


@recycling_note.register
def _(t: Cardboard) -> str:
    return "Cardboard: flatten and bundle"


def main() -> None:
    seen: set[type] = set()
    for t in parse("Trash.dat"):
        if type(t) not in seen:
            seen.add(type(t))
            print(recycling_note(t))


if __name__ == "__main__":
    main()
