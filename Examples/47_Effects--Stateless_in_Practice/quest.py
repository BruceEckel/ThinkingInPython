# quest.py
from typing import Protocol, runtime_checkable
from stateless import Depend, Need, need

@runtime_checkable
class Narrator(Protocol):
    def say(self, line: str) -> None: ...

@runtime_checkable
class Hero(Protocol):
    def name(self) -> str: ...
    def approach(self, obstacle: str) -> str: ...

@runtime_checkable
class Obstacle(Protocol):
    def blocks(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator] | Need[Hero] | Need[Obstacle], None
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    obstacle = yield from need(Obstacle)
    narrator.say(f"{hero.name()} arrives")
    narrator.say(hero.approach(obstacle.blocks()))
