# exercise_10.py
from collections.abc import Callable, Iterable
from enum import Enum, StrEnum
from typing import Protocol
from record import record

# The chapter's state.py, state_machine.py, and
# enum_states.py's StateRow, inlined:
class State(Protocol):
    def run(self) -> None: ...
    def next(self, input_: object, /) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def step(self, input_: object) -> None:
        state = self.current_state
        self.current_state = state.next(input_)
        print(state, input_, "->", self.current_state)
        self.current_state.run()

def run_all(machine: StateMachine,
            inputs: Iterable[object]) -> None:
    for input_ in inputs:
        machine.step(input_)

class Input(StrEnum):
    ANNOY = "annoy"
    CALM = "calm"
    TAKE_PILL = "take pill"

@record
class StateRow:
    message: str
    next: Callable[[object], State]
    def run(self) -> None:
        print(self.message)

def happy(input_: object) -> Mood:
    match input_:
        case Input.ANNOY:
            return Mood.GRUMPY
        case Input.TAKE_PILL:
            return Mood.PROZAC
        case _:
            return Mood.HAPPY

def grumpy(input_: object) -> Mood:
    match input_:
        case Input.CALM:
            return Mood.HAPPY
        case Input.TAKE_PILL:
            return Mood.PROZAC
        case _:
            return Mood.GRUMPY

class Mood(StateRow, Enum):
    HAPPY = ("Great to see you!", happy)
    GRUMPY = ("What do you want?", grumpy)
    PROZAC = ("Everything is wonderful.",
              lambda _: Mood.PROZAC)
    def __str__(self) -> str:
        return self.name.capitalize()

run_all(StateMachine(Mood.HAPPY), [
    Input.ANNOY, Input.CALM, Input.TAKE_PILL, Input.ANNOY])
#: Great to see you!
#: Happy annoy -> Grumpy
#: What do you want?
#: Grumpy calm -> Happy
#: Great to see you!
#: Happy take pill -> Prozac
#: Everything is wonderful.
#: Prozac annoy -> Prozac
#: Everything is wonderful.
print([mood.name for mood in Mood])
#: ['HAPPY', 'GRUMPY', 'PROZAC']
