# exercise_10.py
from collections.abc import Callable
from enum import Enum, auto
from typing import Final
from record import record

class Input(Enum):
    ANNOY = auto()
    CALM = auto()
    TAKE_PILL = auto()

type Behavior = Callable[[Input], str]
type Transition = Callable[[Input], Mood]

@record
class State:
    behavior: Behavior
    transition: Transition

def happy(input_: Input) -> Mood:
    match input_:
        case Input.ANNOY:
            return Mood.GRUMPY
        case Input.TAKE_PILL:
            return Mood.PROZAC
        case _:
            return Mood.HAPPY

def grumpy(input_: Input) -> Mood:
    match input_:
        case Input.CALM:
            return Mood.HAPPY
        case Input.TAKE_PILL:
            return Mood.PROZAC
        case _:
            return Mood.GRUMPY

class Mood(State, Enum):
    HAPPY = (lambda _: "Great to see you!", happy)
    GRUMPY = (lambda _: "What do you want?", grumpy)
    PROZAC = (lambda _: "Everything is wonderful.",
              lambda _: Mood.PROZAC)

class UnpredictablePerson:
    def __init__(self, mood: Mood) -> None:
        self.mood = mood

    def hello(self, input_: Input) -> str:
        self.mood = self.mood.transition(input_)
        return self.mood.behavior(input_)

INPUTS: Final[list[Input]] = [
    Input.ANNOY, Input.CALM, Input.TAKE_PILL, Input.ANNOY,
]
person = UnpredictablePerson(Mood.HAPPY)
for input_ in INPUTS:
    before = person.mood
    greeting = person.hello(input_)
    print(f"{before.name} {input_.name}: {greeting}"
          f" -> {person.mood.name}")
#: HAPPY ANNOY: What do you want? -> GRUMPY
#: GRUMPY CALM: Great to see you! -> HAPPY
#: HAPPY TAKE_PILL: Everything is wonderful. -> PROZAC
#: PROZAC ANNOY: Everything is wonderful. -> PROZAC
print([mood.name for mood in Mood])
#: ['HAPPY', 'GRUMPY', 'PROZAC']
