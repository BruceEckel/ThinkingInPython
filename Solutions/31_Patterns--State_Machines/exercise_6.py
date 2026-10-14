# exercise_6.py
from collections.abc import Callable
from enum import Enum, auto
from exceptions import expect
from record import record
from table_machine import NoTransition, Rule, StateMachine

class WashState(Enum):
    IDLE = auto()
    FILLING = auto()
    WASHING = auto()
    RINSING = auto()
    SPINNING = auto()
    DONE = auto()

@record
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
        rules = [
            Rule(WashState.IDLE, Start, WashState.FILLING,
                 self.begin),
            Rule(WashState.FILLING, Full, WashState.WASHING,
                 self.log_msg("washing")),
            Rule(WashState.WASHING, WashDone,
                 WashState.RINSING,
                 self.log_msg("rinsing")),
            Rule(WashState.RINSING, RinseDone,
                 WashState.SPINNING,
                 self.log_msg("slow spin"), self.too_heavy),
            Rule(WashState.RINSING, RinseDone,
                 WashState.SPINNING,
                 self.log_msg("fast spin")),
            Rule(WashState.SPINNING, SpinDone,
                 WashState.DONE, self.log_msg("done")),
        ]
        super().__init__(WashState.IDLE, rules)

    def begin(self, start: Start) -> None:
        self.load_kg = start.load_kg
        self.log.append("filling")

    def too_heavy(self, input_: RinseDone) -> bool:
        return self.load_kg > 6

    def log_msg(
            self, msg: str) -> Callable[[object], None]:
        def action(input_: object) -> None:
            self.log.append(msg)
        return action

cycle = [Full(), WashDone(), RinseDone(), SpinDone()]
heavy = WashingMachine()
for input_ in [Start(8), *cycle]:
    heavy.handle(input_)
print(heavy.log)
#: ['filling', 'washing', 'rinsing', 'slow spin', 'done']
light = WashingMachine()
for input_ in [Start(3), *cycle]:
    light.handle(input_)
print(light.log)
#: ['filling', 'washing', 'rinsing', 'fast spin', 'done']

# Start pressed again, mid-cycle:
busy = WashingMachine()
busy.handle(Start(3))
expect(NoTransition, busy.handle, Start(5))
#: [NoTransition] no rule from <WashState.FILLING: 2> on
#: Start
print(busy.state.name, busy.load_kg)
#: FILLING 3
