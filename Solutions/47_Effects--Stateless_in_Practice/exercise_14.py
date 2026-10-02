# exercise_14.py
from collections.abc import Callable
from typing import Protocol, runtime_checkable
from stateless import Depend, Need, need, run, supply

@runtime_checkable
class Narrator(Protocol):
    def say(self, line: str) -> None: ...

@runtime_checkable
class Hero(Protocol):
    def name(self) -> str: ...

@runtime_checkable
class Obstacle(Protocol):
    def blocks(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator] | Need[Hero] | Need[Obstacle], None
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    obstacle = yield from need(Obstacle)
    blocker = obstacle.blocks()
    narrator.say(f"{hero.name()} meets the {blocker}")

class Kitty:
    def name(self) -> str: return "Kitty"

class Puzzle:
    def blocks(self) -> str: return "puzzle"

class Warrior:
    def name(self) -> str: return "Warrior"

class Weapon:
    def blocks(self) -> str: return "nasty weapon"

class Loud:
    def say(self, line: str) -> None: print(line)

def play(
    narrator: Narrator, hero: Hero, obstacle: Obstacle
) -> None:
    run(supply(narrator, hero, obstacle)(encounter)())

def kitties(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle())

def warriors(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon())

type Cast = Callable[[Narrator], None]

def run_season(casts: list[Cast]) -> None:
    for cast in casts:
        cast(Loud())

run_season([kitties, warriors])
#: Kitty meets the puzzle
#: Warrior meets the nasty weapon
play(Loud(), Kitty(), Weapon())
#: Kitty meets the nasty weapon
