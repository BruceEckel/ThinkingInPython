# games2.py
# Simplified Abstract Factory.
from typing import Any

class Kitty:
    def interact_with(self, obstacle: Any) -> None:
        print("Kitty has encountered a", obstacle.action())

class Warrior:
    def interact_with(self, obstacle: Any) -> None:
        print("Warrior now battles a", obstacle.action())

class Puzzle:
    def action(self) -> str: return "Puzzle"

class NastyWeapon:
    def action(self) -> str: return "NastyWeapon"

# Concrete factories:
class KittiesAndPuzzles:
    def make_character(self) -> Kitty: return Kitty()
    def make_obstacle(self) -> Puzzle: return Puzzle()

class WarriorsAndWeapons:
    def make_character(self) -> Warrior: return Warrior()
    def make_obstacle(self) -> NastyWeapon: return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory: Any) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self) -> None:
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
g1.play()
## Kitty has encountered a Puzzle
g2.play()
## Warrior now battles a NastyWeapon
