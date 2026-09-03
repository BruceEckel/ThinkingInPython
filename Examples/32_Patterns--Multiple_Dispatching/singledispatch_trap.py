# singledispatch_trap.py
from functools import singledispatchmethod

class Item:
    @singledispatchmethod
    def compete(self, item: object) -> str:
        raise NotImplementedError

class Paper(Item):
    pass

class Rock(Item):
    pass

@Paper.compete.register  # type: ignore
def _(self: Item, item: Rock) -> str:
    return "paper wins"

@Rock.compete.register  # type: ignore
def _(self: Item, item: Rock) -> str:
    return "rock draws"

print(Paper().compete(Rock()))
#: rock draws
print(Rock().compete(Rock()))
#: rock draws
