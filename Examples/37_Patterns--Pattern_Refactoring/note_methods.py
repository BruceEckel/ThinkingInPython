# note_methods.py
from record import record

@record
class Trash:
    weight: float

    def note(self) -> str:
        return f"{type(self).__name__}: nothing special"

    # New requirement, so a new method here
    def hazard(self) -> str:
        return "none"

class Aluminum(Trash):
    def note(self) -> str:
        return "Aluminum: crush and bale"

    def hazard(self) -> str:
        return "sharp edges"

class Glass(Trash):
    def note(self) -> str:
        return "Glass: sort by color, then crush"

    def hazard(self) -> str:
        return "sharp edges"

class Cardboard(Trash):
    def note(self) -> str:
        return "Cardboard: flatten and bundle"

materials = [Aluminum, Glass, Cardboard]
for material in materials:
    piece = material(1.0)
    print(f"{piece.note()} | hazard: {piece.hazard()}")
#: Aluminum: crush and bale | hazard: sharp edges
#: Glass: sort by color, then crush | hazard: sharp edges
#: Cardboard: flatten and bundle | hazard: none
edited = [c for c in materials  # [1]
          if "hazard" in c.__dict__]
print(f"classes edited for one operation: {len(edited)}")
#: classes edited for one operation: 2
