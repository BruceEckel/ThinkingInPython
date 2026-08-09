# exercise_2.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass
class Rose(Flower):  # The new type: 2 lines
    pass

@singledispatch
def nectar(flower: Flower) -> str:
    return f"{flower}: no nectar"

@nectar.register
def _(flower: Rose) -> str:  # 3 lines
    return f"{flower}: abundant nectar"

@singledispatch
def fragrance(flower: Flower) -> str:
    return "faint"

@fragrance.register
def _(flower: Rose) -> str:  # 3 lines
    return "strong"

@singledispatch  # The new operation: 3 lines
def thorns(flower: Flower) -> str:
    return "none"

@thorns.register
def _(flower: Rose) -> str:  # 3 lines
    return "sharp"

rose = Rose()
print(nectar(rose), "/", fragrance(rose), "/", thorns(rose))
#: Rose: abundant nectar / strong / sharp
print(thorns(Gladiolus()))
#: none
