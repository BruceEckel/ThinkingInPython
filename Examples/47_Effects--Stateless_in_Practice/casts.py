# casts.py
from quest import Hero, Narrator, Obstacle, encounter
from stateless import run, supply

class Kitty:
    def name(self) -> str: return "Kitty"
    def approach(self, obstacle: str) -> str:
        return f"and bats at the {obstacle}"

class Puzzle:
    def blocks(self) -> str: return "puzzle"

class Warrior:
    def name(self) -> str: return "Warrior"
    def approach(self, obstacle: str) -> str:
        return f"and battles the {obstacle}"

class Weapon:
    def blocks(self) -> str: return "nasty weapon"

def play(
    narrator: Narrator, hero: Hero, obstacle: Obstacle
) -> None:
    cast = supply(narrator, hero, obstacle)
    run(cast(encounter)())

def kitties_and_puzzles(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle())

def warriors_and_weapons(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon())
