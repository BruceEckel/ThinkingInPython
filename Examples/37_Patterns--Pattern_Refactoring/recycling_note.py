# recycling_note.py
from functools import singledispatch
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

for cls in Trash.registry.values():
    print(recycling_note(cls(1.0)))
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
