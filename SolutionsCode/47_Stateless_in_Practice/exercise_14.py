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
class Reward(Protocol):
    def prize(self) -> str: ...

def encounter() -> Depend[
    Need[Narrator] | Need[Hero] | Need[Reward], None
]:
    narrator = yield from need(Narrator)
    hero = yield from need(Hero)
    reward = yield from need(Reward)
    narrator.say(f"{hero.name()} wins {reward.prize()}")

class Kitty:
    def name(self) -> str: return "Kitty"

class Yarn:
    def prize(self) -> str: return "a ball of yarn"

class Warrior:
    def name(self) -> str: return "Warrior"

class Gold:
    def prize(self) -> str: return "a chest of gold"

class Loud:
    def say(self, line: str) -> None: print(line)

def play(
    narrator: Narrator, hero: Hero, reward: Reward
) -> None:
    run(supply(narrator, hero, reward)(encounter)())

def kitties(narrator: Narrator) -> None:
    play(narrator, Kitty(), Yarn())

def warriors(narrator: Narrator) -> None:
    play(narrator, Warrior(), Gold())

type Cast = Callable[[Narrator], None]

def run_season(casts: list[Cast]) -> None:
    for cast in casts:
        cast(Loud())

run_season([kitties, warriors])
#: Kitty wins a ball of yarn
#: Warrior wins a chest of gold
play(Loud(), Kitty(), Gold())
#: Kitty wins a chest of gold
