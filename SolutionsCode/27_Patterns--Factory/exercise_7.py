# exercise_7.py
import copy
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)
    parts: dict[str, int] = field(default_factory=dict)

PROTOTYPES: Final[dict[str, Monster]] = {
    "goblin": Monster("Goblin", hp=10, powers=["bite"],
                      parts={"arms": 2}),
    "hydra": Monster("Hydra", hp=60, powers=["bite"],
                     parts={"heads": 9}),
}

def shallow_spawn(kind: str) -> Monster:
    return copy.copy(PROTOTYPES[kind])  # The bug

a = shallow_spawn("hydra")
a.parts["heads"] = 1  # Cut off eight heads
print(PROTOTYPES["hydra"].parts)  # The prototype changed
#: {'heads': 1}
# So does every later spawn
print(shallow_spawn("hydra").parts)
#: {'heads': 1}
