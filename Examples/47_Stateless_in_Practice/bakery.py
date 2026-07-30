# bakery.py
from dataclasses import dataclass
from stateless import Depend, Need, need, run, supply

@dataclass(frozen=True)
class Dough:
    flour: str
    def risen(self) -> str:
        print("dough: risen")
        return f"{self.flour} dough"

@dataclass(frozen=True)
class Oven:
    celsius: int
    def bake(self, dough: str) -> str:
        print(f"oven: baking at {self.celsius}")
        return f"loaf of {dough}"

@dataclass(frozen=True)
class Toaster:
    setting: int
    def brown(self, loaf: str) -> str:
        print(f"toaster: setting {self.setting}")
        return f"toasted {loaf}"

def bread() -> Depend[Need[Dough] | Need[Oven], str]:
    dough = yield from need(Dough)
    oven = yield from need(Oven)
    return oven.bake(dough.risen())

def toast() -> Depend[
    Need[Dough] | Need[Oven] | Need[Toaster], str
]:
    loaf = yield from bread()
    toaster = yield from need(Toaster)
    return toaster.brown(loaf)

kitchen = supply(Dough("rye"), Oven(220), Toaster(3))
print(run(kitchen(toast)()))
#: dough: risen
#: oven: baking at 220
#: toaster: setting 3
#: toasted loaf of rye dough
