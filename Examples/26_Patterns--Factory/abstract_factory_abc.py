# abstract_factory_abc.py
from abc import ABC, abstractmethod
from typing import override

class Obstacle(ABC):
    @abstractmethod
    def description(self) -> str: ...

class Character(ABC):
    @abstractmethod
    def interact_with(self, obstacle: Obstacle) -> None: ...

class Kitty(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty encounters a", obstacle.description())

class Warrior(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior battles a", obstacle.description())

class Puzzle(Obstacle):
    @override
    def description(self) -> str:
        return "Puzzle"

class Weapon(Obstacle):
    @override
    def description(self) -> str:
        return "Weapon"

# The Abstract Factory:
class GameElementFactory(ABC):
    @abstractmethod
    def make_character(self) -> Character: ...
    @abstractmethod
    def make_obstacle(self) -> Obstacle: ...

# Concrete factories:
class KittiesAndPuzzles(GameElementFactory):
    @override
    def make_character(self) -> Character: return Kitty()
    @override
    def make_obstacle(self) -> Obstacle: return Puzzle()

class WarriorsAndWeapons(GameElementFactory):
    @override
    def make_character(self) -> Character: return Warrior()
    @override
    def make_obstacle(self) -> Obstacle: return Weapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
g1.play()
#: Kitty encounters a Puzzle
g2.play()
#: Warrior battles a Weapon
