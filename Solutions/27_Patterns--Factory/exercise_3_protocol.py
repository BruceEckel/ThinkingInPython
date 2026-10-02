# exercise_3_protocol.py
from typing import Protocol

class Obstacle(Protocol):
    def description(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)

class Gnome:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.description())

class Fairy:
    def description(self) -> str: return "Fairy"

class GnomesAndFairies:  # Declares no base class
    def make_character(self) -> Gnome: return Gnome()
    def make_obstacle(self) -> Fairy: return Fairy()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Fairy
