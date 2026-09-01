# games2.py
# Simplified Abstract Factory.
from typing import Protocol

class Obstacle(Protocol):
    def description(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class Kitty:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty has encountered a",
              obstacle.description())

class Warrior:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior now battles a",
              obstacle.description())

class Puzzle:
    def description(self) -> str: return "Puzzle"

class Weapon:
    def description(self) -> str: return "Weapon"

# Concrete factories:
class KittiesAndPuzzles:
    def make_character(self) -> Kitty: return Kitty()
    def make_obstacle(self) -> Puzzle: return Puzzle()

class WarriorsAndWeapons:
    def make_character(self) -> Warrior: return Warrior()
    def make_obstacle(self) -> Weapon: return Weapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)

class BrokenFactory:
    def make_character(self) -> Kitty: return Kitty()

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
# ty: expected "GameElementFactory", found "BrokenFactory":
# GameEnvironment(BrokenFactory())
g1.play()
#: Kitty has encountered a Puzzle
g2.play()
#: Warrior now battles a Weapon
