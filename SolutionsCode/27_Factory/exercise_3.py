# exercise_3.py
class Obstacle:
    def action(self) -> str:
        raise NotImplementedError

class Character:
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory:
    def make_character(self) -> Character:
        raise NotImplementedError

    def make_obstacle(self) -> Obstacle:
        raise NotImplementedError

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()

    def play(self) -> None:
        self.p.interact_with(self.ob)

class Gnome(Character):
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.action())

class Riddle(Obstacle):
    def action(self) -> str:
        return "Riddle"

class GnomesAndFairies(GameElementFactory):
    def make_character(self) -> Character:
        return Gnome()

    def make_obstacle(self) -> Obstacle:
        return Riddle()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Riddle
