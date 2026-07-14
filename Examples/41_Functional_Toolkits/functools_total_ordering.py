# functools_total_ordering.py
from functools import total_ordering

@total_ordering
class Weight:
    def __init__(self, kg: float) -> None:
        self.kg = kg

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Weight) and self.kg == other.kg

    def __lt__(self, other: Weight) -> bool:
        return self.kg < other.kg

light = Weight(2)
heavy = Weight(5)
print(light < heavy, light <= heavy, light > heavy)
#: True True False
