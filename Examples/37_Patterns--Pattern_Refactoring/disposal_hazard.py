# disposal_hazard.py
from functools import singledispatch
from trash import Aluminum, Glass, Trash

@singledispatch
def hazard(piece: Trash) -> str:
    return "none"

@hazard.register
def _(piece: Aluminum) -> str:
    return "sharp edges"

@hazard.register
def _(piece: Glass) -> str:
    return "sharp edges"

for material in Trash.registry.values():
    print(f"{material.__name__}: {hazard(material(1.0))}")
#: Aluminum: sharp edges
#: Paper: none
#: Glass: sharp edges
#: Cardboard: none
edited = [c for c in Trash.registry.values()
          if "hazard" in c.__dict__]
print(f"classes edited for one operation: {len(edited)}")
#: classes edited for one operation: 0
