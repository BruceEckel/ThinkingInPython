# recycling_note.py
from functools import singledispatch
from trash import Aluminum, Cardboard, Glass, Trash

@singledispatch
def recycling_note(piece: Trash) -> str:
    return f"{type(piece).__name__}: no special handling"

@recycling_note.register
def _(piece: Aluminum) -> str:
    return "Aluminum: crush and bale"

@recycling_note.register
def _(piece: Glass) -> str:
    return "Glass: sort by color, then crush"

@recycling_note.register
def _(piece: Cardboard) -> str:
    return "Cardboard: flatten and bundle"

for material in Trash.registry.values():
    print(recycling_note(material(1.0)))
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
