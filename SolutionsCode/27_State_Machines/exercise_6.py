# exercise_6.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class MoodState(Enum):
    HAPPY = auto()
    GRUMPY = auto()
    PROZAC = auto()

class TakePill:
    pass
class Annoy:
    pass
class Calm:
    pass

class MoodMachine(StateMachine):
    def __init__(self) -> None:
        self.message = ""
        happy_takes_pill = (
            None, self.say("Everything is wonderful."),
            MoodState.PROZAC)
        table: Table = {
            (MoodState.HAPPY, Annoy): [(
                None, self.say("What do you want?"),
                MoodState.GRUMPY)],
            (MoodState.GRUMPY, Calm): [(
                None, self.say("Great to see you!"),
                MoodState.HAPPY)],
            (MoodState.HAPPY, TakePill): [happy_takes_pill],
            (MoodState.GRUMPY, TakePill): [happy_takes_pill],
        }
        super().__init__(MoodState.HAPPY, table)

    def say(self, msg: str):
        def action(event: object) -> None:
            self.message = msg
        return action

mm = MoodMachine()
mm.handle(Annoy())
print(mm.state, mm.message)
#: MoodState.GRUMPY What do you want?
mm.handle(TakePill())
print(mm.state, mm.message)
#: MoodState.PROZAC Everything is wonderful.
