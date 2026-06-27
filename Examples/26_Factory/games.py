# games.py
# An example of the Abstract Factory pattern.
from typing import override

class Obstacle:
    def action(self) -> str:
        raise NotImplementedError

class Character:
    def interact_with(self, obstacle: Obstacle) -> None: ...

class Kitty(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty has encountered a", obstacle.action())

class Warrior(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior now battles a", obstacle.action())

class Puzzle(Obstacle):
    @override
    def action(self) -> str:
        return "Puzzle"

class NastyWeapon(Obstacle):
    @override
    def action(self) -> str:
        return "NastyWeapon"

# The Abstract Factory:
class GameElementFactory:
    def make_character(self) -> Character:
        raise NotImplementedError
    def make_obstacle(self) -> Obstacle:
        raise NotImplementedError

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
    def make_obstacle(self) -> Obstacle: return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self) -> None:
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
g1.play()
#: Kitty has encountered a Puzzle
g2.play()
#: Warrior now battles a NastyWeapon
