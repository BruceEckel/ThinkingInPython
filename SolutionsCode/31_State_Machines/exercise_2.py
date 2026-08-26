# exercise_2.py
from dataclasses import dataclass
from enum import Enum, auto
from table_machine import StateMachine, Table

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

@dataclass
class Start:
    load_kg: float

class Full:
    pass
class WashDone:
    pass
class RinseDone:
    pass
class SpinDone:
    pass

class WashingMachine(StateMachine):
    def __init__(self) -> None:
        self.load_kg = 0.0
        self.log: list[str] = []
        table: Table = {
            (WashState.IDLE, Start):
                [(None, self.begin, WashState.FILLING)],
            (WashState.FILLING, Full):
                [(None, self.log_msg("washing"),
                  WashState.WASHING)],
            (WashState.WASHING, WashDone):
                [(None, self.log_msg("rinsing"),
                  WashState.RINSING)],
            (WashState.RINSING, RinseDone): [
                (self.too_heavy, self.log_msg("slow spin"),
                 WashState.SPINNING),
                (None, self.log_msg("fast spin"),
                 WashState.SPINNING),
            ],
            (WashState.SPINNING, SpinDone):
                [(None, self.log_msg("done"),
                  WashState.DONE)],
        }
        super().__init__(WashState.IDLE, table)

    def begin(self, start: Start) -> None:
        self.load_kg = start.load_kg
        self.log.append("filling")

    def too_heavy(self, event: RinseDone) -> bool:
        return self.load_kg > 6

    def log_msg(self, msg: str):
        def action(event: object) -> None:
            self.log.append(msg)
        return action

cycle = [Full(), WashDone(), RinseDone(), SpinDone()]
heavy = WashingMachine()
for event in [Start(8), *cycle]:
    heavy.handle(event)
print(heavy.log)
#: ['filling', 'washing', 'rinsing', 'slow spin', 'done']
light = WashingMachine()
for event in [Start(3), *cycle]:
    light.handle(event)
print(light.log)
#: ['filling', 'washing', 'rinsing', 'fast spin', 'done']
