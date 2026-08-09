# exercise_13.py
from dataclasses import dataclass
from kitchen import Dough, Oven, Toaster, toast
from stateless import Depend, Need, need, run, supply

@dataclass(frozen=True)
class Butter:
    grams: int
    def spread(self, slice_: str) -> str:
        print(f"butter: {self.grams}g")
        return f"buttered {slice_}"

def buttered() -> Depend[
    Need[Dough] | Need[Oven] | Need[Toaster] | Need[Butter], str
]:
    slice_ = yield from toast()
    butter = yield from need(Butter)
    return butter.spread(slice_)

kitchen = supply(Dough("rye"), Oven(220), Toaster(3), Butter(10))
print(run(kitchen(buttered)()))
#: dough: risen
#: oven: baking at 220
#: toaster: setting 3
#: butter: 10g
#: buttered toasted loaf of rye dough
