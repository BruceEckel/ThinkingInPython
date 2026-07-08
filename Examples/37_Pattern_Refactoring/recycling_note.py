# recycling_note.py
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

seen: set[type[Trash]] = set()
for t in parse("trash.dat"):
    if type(t) not in seen:
        seen.add(type(t))
        print(recycling_note(t))
#: Glass: sort by color, then crush
#: Paper: no special handling
#: Aluminum: crush and bale
#: Cardboard: flatten and bundle
