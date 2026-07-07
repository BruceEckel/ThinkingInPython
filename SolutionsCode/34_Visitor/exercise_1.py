# exercise_1.py
import random
from typing import Any

class Inhabitant:
    def interact(self, other: Any) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__

class Dwarf(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (engineer) negotiates with {other}"

class Elf(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (marketer) pitches to {other}"

class Troll(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (manager) directs {other}"

class Project:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def gather(self, n: int) -> list[Inhabitant]:
        kinds = [Dwarf, Elf, Troll]
        return [self.rng.choice(kinds)() for _ in range(n)]

project = Project(seed=1)
team = project.gather(4)
for a, b in zip(team, team[1:]):
    print(a.interact(b))
#: Dwarf (engineer) negotiates with Troll
#: Troll (manager) directs Dwarf
#: Dwarf (engineer) negotiates with Elf
