# prototype_registry.py
import copy
from dataclasses import dataclass, field
from typing import Final, Literal

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

type Kind = Literal["goblin", "troll"]

PROTOTYPES: Final[dict[Kind, Monster]] = {
    "goblin": Monster("Goblin", hp=10, powers=["bite"]),
    "troll": Monster("Troll", hp=40,
                     powers=["smash", "regen"]),
}

def spawn(kind: Kind) -> Monster:
    return copy.deepcopy(PROTOTYPES[kind])
