# games2.py
# Simplified Abstract Factory.
from typing import Any


class Kitty:
    def interact_with(self, obstacle: Any) -> None:
        print("Kitty has encountered a",
        obstacle.action())

class KungFuGuy:
    def interact_with(self, obstacle: Any) -> None:
        print("KungFuGuy now battles a",
        obstacle.action())

class Puzzle:
    def action(self) -> None: print("Puzzle")

class NastyWeapon:
    def action(self) -> None: print("NastyWeapon")

# Concrete factories:
class KittiesAndPuzzles:
    def make_character(self) -> Kitty: return Kitty()
    def make_obstacle(self) -> Puzzle: return Puzzle()

class KillAndDismember:
    def make_character(self) -> KungFuGuy: return KungFuGuy()
    def make_obstacle(self) -> NastyWeapon: return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory: Any) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self) -> None:
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(KillAndDismember())
g1.play()
g2.play()
