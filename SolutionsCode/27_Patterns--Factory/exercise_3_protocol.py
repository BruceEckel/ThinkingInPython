# exercise_3_protocol.py
from typing import Protocol

class Obstacle(Protocol):
    def description(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class Gnome:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.description())

class Riddle:
    def description(self) -> str: return "Riddle"

class GnomesAndFairies:  # Declares no base class
    def make_character(self) -> Gnome: return Gnome()
    def make_obstacle(self) -> Riddle: return Riddle()

def play(factory: GameElementFactory) -> None:
    factory.make_character().interact_with(
        factory.make_obstacle())

play(GnomesAndFairies())
#: Gnome discovers a Riddle
