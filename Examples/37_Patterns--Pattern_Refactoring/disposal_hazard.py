# disposal_hazard.py
from functools import singledispatch
from trash import Aluminum, Glass, Trash

@singledispatch
def hazard(t: Trash) -> str:
    return "none"

@hazard.register
def _(t: Aluminum) -> str:
    return "sharp edges"

@hazard.register
def _(t: Glass) -> str:
    return "sharp edges"

for cls in Trash.registry.values():
    print(f"{cls.__name__}: {hazard(cls(1.0))}")
edited = [c for c in Trash.registry.values()
          if "hazard" in c.__dict__]
print(f"classes edited for one operation: {len(edited)}")
#: Aluminum: sharp edges
#: Paper: none
#: Glass: sharp edges
#: Cardboard: none
#: classes edited for one operation: 0
