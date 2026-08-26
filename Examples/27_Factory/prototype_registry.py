# prototype_registry.py
import copy
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

PROTOTYPES: Final[dict[str, Monster]] = {
    "goblin": Monster("Goblin", hp=10, powers=["bite"]),
    "troll": Monster("Troll", hp=40,
                     powers=["smash", "regen"]),
}

def spawn(kind: str) -> Monster:
    return copy.deepcopy(PROTOTYPES[kind])

if __name__ == "__main__":
    a = spawn("goblin")
    b = spawn("goblin")
    b.hp = 5
    print(a.hp, b.hp)  # The copies are independent
    print(spawn("troll"))
#: 10 5
#: Monster(name='Troll', hp=40, powers=['smash', 'regen'])
