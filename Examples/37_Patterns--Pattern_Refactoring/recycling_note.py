# recycling_note.py
from functools import singledispatch
from trash import Aluminum, Cardboard, Glass, Trash

@singledispatch
def recycling_note(piece: Trash) -> str:
    return "no special handling"

@recycling_note.register
def _(piece: Aluminum) -> str:
    return "crush and bale"

@recycling_note.register
def _(piece: Glass) -> str:
    return "sort by color, then crush"

@recycling_note.register
def _(piece: Cardboard) -> str:
    return "flatten and bundle"

for material in Trash.registry.values():
    note = recycling_note(material(1.0))
    print(f"{material.__name__}: {note}")
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
