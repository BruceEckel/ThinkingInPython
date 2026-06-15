# visit_singledispatch.py
# Adding operations to a fixed hierarchy without touching it, the
# Python way.
from functools import singledispatch


class Flower:
    def __str__(self) -> str:
        return type(self).__name__


class Gladiolus(Flower): pass
class Runuculus(Flower): pass
class Chrysanthemum(Flower): pass


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
def _(flower: Runuculus) -> str:
    return "strong"


flowers: list[Flower] = [Gladiolus(), Runuculus(), Chrysanthemum()]
for f in flowers:
    print(nectar(f), "| fragrance:", fragrance(f))
