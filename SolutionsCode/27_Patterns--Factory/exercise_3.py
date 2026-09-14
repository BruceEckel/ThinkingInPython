# exercise_3.py
from abc import ABC, abstractmethod
from typing import override

class Obstacle(ABC):
    @abstractmethod
    def description(self) -> str: ...

class Character(ABC):
    @abstractmethod
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(ABC):
    @abstractmethod
    def make_character(self) -> Character: ...

    @abstractmethod
    def make_obstacle(self) -> Obstacle: ...

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()

    def play(self) -> None:
        self.p.interact_with(self.ob)

class Gnome(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.description())

class Riddle(Obstacle):
    @override
    def description(self) -> str:
        return "Riddle"

class GnomesAndFairies(GameElementFactory):
    @override
    def make_character(self) -> Character:
        return Gnome()

    @override
    def make_obstacle(self) -> Obstacle:
        return Riddle()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Riddle
