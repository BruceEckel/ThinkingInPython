# games.py
# An example of the Abstract Factory pattern.

class Obstacle:
    def action(self) -> None: pass

class Character:
    def interact_with(self, obstacle: Obstacle) -> None: pass

class Kitty(Character):
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty has encountered a",
        obstacle.action())

class KungFuGuy(Character):
    def interact_with(self, obstacle: Obstacle) -> None:
        print("KungFuGuy now battles a",
        obstacle.action())

class Puzzle(Obstacle):
    def action(self) -> None:
        print("Puzzle")

class NastyWeapon(Obstacle):
    def action(self) -> None:
        print("NastyWeapon")

# The Abstract Factory:
class GameElementFactory:
    def make_character(self) -> Character:
        raise NotImplementedError
    def make_obstacle(self) -> Obstacle:
        raise NotImplementedError

# Concrete factories:
class KittiesAndPuzzles(GameElementFactory):
    def make_character(self) -> Character: return Kitty()
    def make_obstacle(self) -> Obstacle: return Puzzle()

class KillAndDismember(GameElementFactory):
    def make_character(self) -> Character: return KungFuGuy()
    def make_obstacle(self) -> Obstacle: return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self) -> None:
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(KillAndDismember())
g1.play()
g2.play()
