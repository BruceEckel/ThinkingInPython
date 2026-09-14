# exercise_11.py
import copy
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

type Builder = Callable[[], Monster]

PROTOTYPES: Final[dict[str, Monster]] = {}

def prototype(name: str) -> Callable[[Builder], Builder]:
    def register(build: Builder) -> Builder:
        PROTOTYPES[name] = build()
        return build
    return register

@prototype("goblin")
def goblin() -> Monster:
    return Monster("Goblin", hp=10, powers=["bite"])

@prototype("troll")
def troll() -> Monster:
    return Monster("Troll", hp=40,
                   powers=["smash", "regen"])

def spawn(name: str) -> Monster:
    return copy.deepcopy(PROTOTYPES[name])

print(sorted(PROTOTYPES))
#: ['goblin', 'troll']
a = spawn("goblin")
b = spawn("goblin")
b.hp = 5
print(a.hp, b.hp)
#: 10 5
print(spawn("troll"))
#: Monster(name='Troll', hp=40, powers=['smash', 'regen'])
