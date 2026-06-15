# games2.py
# Simplified Abstract Factory.

class Kitty:
    def interact_with(self, obstacle):
        print("Kitty has encountered a",
        obstacle.action())

class KungFuGuy:
    def interact_with(self, obstacle):
        print("KungFuGuy now battles a",
        obstacle.action())

class Puzzle:
    def action(self): print("Puzzle")

class NastyWeapon:
    def action(self): print("NastyWeapon")

# Concrete factories:
class KittiesAndPuzzles:
    def make_character(self): return Kitty()
    def make_obstacle(self): return Puzzle()

class KillAndDismember:
    def make_character(self): return KungFuGuy()
    def make_obstacle(self): return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory):
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self):
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(KillAndDismember())
g1.play()
g2.play()
