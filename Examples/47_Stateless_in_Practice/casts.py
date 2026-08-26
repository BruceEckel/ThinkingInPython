# casts.py
from quest import (Hero, Narrator, Obstacle, Reward,
                   Terrain, encounter)
from stateless import run, supply

class Kitty:
    def name(self) -> str: return "Kitty"
    def approach(self, obstacle: str) -> str:
        return f"and bats at the {obstacle}"

class Puzzle:
    def blocks(self) -> str: return "puzzle"

class Garden:
    def underfoot(self) -> str: return "garden path"

class Yarn:
    def prize(self) -> str: return "a ball of yarn"

class Warrior:
    def name(self) -> str: return "Warrior"
    def approach(self, obstacle: str) -> str:
        return f"and battles the {obstacle}"

class Weapon:
    def blocks(self) -> str: return "nasty weapon"

class Wasteland:
    def underfoot(self) -> str: return "cracked wasteland"

class Gold:
    def prize(self) -> str: return "a chest of gold"

def play(
    narrator: Narrator,
    hero: Hero,
    obstacle: Obstacle,
    terrain: Terrain,
    reward: Reward,
) -> None:
    cast = supply(narrator, hero, obstacle, terrain, reward)
    run(cast(encounter)())

def kitties_and_puzzles(narrator: Narrator) -> None:
    play(narrator, Kitty(), Puzzle(), Garden(), Yarn())

def warriors_and_weapons(narrator: Narrator) -> None:
    play(narrator, Warrior(), Weapon(), Wasteland(), Gold())
