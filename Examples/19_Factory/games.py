# games.py
# An example of the Abstract Factory pattern.

class Obstacle:
    def action(self): pass

class Character:
    def interact_with(self, obstacle): pass

class Kitty(Character):
    def interact_with(self, obstacle):
        print("Kitty has encountered a",
        obstacle.action())

class KungFuGuy(Character):
    def interact_with(self, obstacle):
        print("KungFuGuy now battles a",
        obstacle.action())

class Puzzle(Obstacle):
    def action(self):
        print("Puzzle")

class NastyWeapon(Obstacle):
    def action(self):
        print("NastyWeapon")

# The Abstract Factory:
class GameElementFactory:
    def make_character(self): pass
    def make_obstacle(self): pass

# Concrete factories:
class KittiesAndPuzzles(GameElementFactory):
    def make_character(self): return Kitty()
    def make_obstacle(self): return Puzzle()

class KillAndDismember(GameElementFactory):
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
