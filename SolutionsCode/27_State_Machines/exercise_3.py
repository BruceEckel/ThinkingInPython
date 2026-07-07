# exercise_3.py
from enum import Enum, auto
from state_machine import StateMachine, Table

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

class Start:
    pass
class Full:
    pass
class WashDone:
    pass
class RinseDone:
    pass
class SpinDone:
    pass
class Reset:
    pass

class WashingMachine(StateMachine):
    def __init__(self) -> None:
        self.log: list[str] = []
        table: Table = {
            (WashState.IDLE, Start):
                [(None, self.log_msg("filling"), WashState.FILLING)],
            (WashState.FILLING, Full):
                [(None, self.log_msg("washing"), WashState.WASHING)],
            (WashState.WASHING, WashDone):
                [(None, self.log_msg("rinsing"), WashState.RINSING)],
            (WashState.RINSING, RinseDone): [(
                None, self.log_msg("spinning"), WashState.SPINNING)],
            (WashState.SPINNING, SpinDone):
                [(None, self.log_msg("done"), WashState.DONE)],
            (WashState.DONE, Reset):
                [(None, self.log_msg("idle"), WashState.IDLE)],
        }
        super().__init__(WashState.IDLE, table)

    def log_msg(self, msg: str):
        def action(event: object) -> None:
            self.log.append(msg)
        return action

wm = WashingMachine()
events = [
    Start(), Full(), WashDone(), RinseDone(), SpinDone(), Reset()]
for event in events:
    wm.handle(event)
print(wm.log)
#: ['filling', 'washing', 'rinsing', 'spinning', 'done', 'idle']
