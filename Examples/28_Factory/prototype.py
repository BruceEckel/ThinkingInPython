# prototype.py
import copy
from dataclasses import dataclass, field

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

    def clone(self) -> Monster:
        return copy.deepcopy(self)

goblin = Monster("Goblin", hp=10, powers=["bite"])
# Build a variant by cloning and adjusting, not rebuilding:
captain = goblin.clone()
captain.name = "Goblin Captain"
captain.hp = 20
captain.powers.append("rally")
print(goblin)
#: Monster(name='Goblin', hp=10, powers=['bite'])
print(captain)
#: Monster(name='Goblin Captain', hp=20, powers=['bite', 'rally'])
