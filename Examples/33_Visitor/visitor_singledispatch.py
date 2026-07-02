# visitor_singledispatch.py
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

# A new operation, defined entirely outside the Flower hierarchy:
@singledispatch
def nectar(flower: Flower) -> str:
    return f"{flower}: no nectar"

@nectar.register
def _(flower: Gladiolus) -> str:
    return f"{flower}: abundant nectar"

@nectar.register
def _(flower: Chrysanthemum) -> str:
    return f"{flower}: a little nectar"

# A second operation, added independently of the first:
@singledispatch
def fragrance(flower: Flower) -> str:
    return "faint"

@fragrance.register
def _(flower: Ranunculus) -> str:
    return "strong"

if __name__ == "__main__":
    flowers: list[Flower] = [
        Gladiolus(), Ranunculus(), Chrysanthemum()]
    for f in flowers:
        print(nectar(f), "| fragrance:", fragrance(f))
#: Gladiolus: abundant nectar | fragrance: faint
#: Ranunculus: no nectar | fragrance: strong
#: Chrysanthemum: a little nectar | fragrance: faint
