# note_methods.py
from dataclasses import dataclass
from typing import ClassVar

@dataclass(frozen=True)
class Trash:
    weight: float
    value: ClassVar[float] = 0.0

    def note(self) -> str:
        return f"{type(self).__name__}: nothing special"

    # New requirement, so a new method here
    def hazard(self) -> str:
        return "none"

class Aluminum(Trash):
    value = 1.67

    def note(self) -> str:
        return "Aluminum: crush and bale"

    def hazard(self) -> str:
        return "sharp edges"

class Glass(Trash):
    value = 0.23

    def note(self) -> str:
        return "Glass: sort by color, then crush"

    def hazard(self) -> str:
        return "sharp edges"

class Cardboard(Trash):
    value = 0.79

    def note(self) -> str:
        return "Cardboard: flatten and bundle"

    def hazard(self) -> str:
        return "none"

materials = [Aluminum, Glass, Cardboard]
for cls in materials:
    t = cls(1.0)
    print(f"{t.note()} | hazard: {t.hazard()}")
edited = [c for c in materials if "hazard" in c.__dict__]
print(f"classes edited for one operation: {len(edited)}")
#: Aluminum: crush and bale | hazard: sharp edges
#: Glass: sort by color, then crush | hazard: sharp edges
#: Cardboard: flatten and bundle | hazard: none
#: classes edited for one operation: 3
