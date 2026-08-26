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

@runtime_checkable
class Terrain(Protocol):
    def underfoot(self) -> str: ...

@runtime_checkable
class Reward(Protocol):
    def prize(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator]
    | Need[Hero]
    | Need[Obstacle]
    | Need[Terrain]
    | Need[Reward],
    None,
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    terrain = yield from need(Terrain)
    obstacle = yield from need(Obstacle)
    reward = yield from need(Reward)
    narrator.say(
        f"{hero.name()} crosses the {terrain.underfoot()}")
    narrator.say(hero.approach(obstacle.blocks()))
    narrator.say(f"and wins {reward.prize()}")
