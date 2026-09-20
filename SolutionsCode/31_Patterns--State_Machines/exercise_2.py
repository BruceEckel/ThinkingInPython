# exercise_2.py
from collections.abc import Iterable
from typing import Protocol

# The chapter's state.py and state_machine.py, inlined:
class State(Protocol):
    def run(self) -> None: ...
    def next(self, event: object) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def run_all(self, inputs: Iterable[object]) -> None:
        for event in inputs:
            print(event)
            self.current_state = (
                self.current_state.next(event))
            self.current_state.run()

class TakePill:
    def __repr__(self) -> str:
        return "TakePill"

class Annoy:
    def __repr__(self) -> str:
        return "Annoy"

class Calm:
    def __repr__(self) -> str:
        return "Calm"

class Happy:
    def run(self) -> None:
        print("Great to see you!")
    def next(self, event: object) -> State:
        if isinstance(event, Annoy):
            return Grumpy()
        if isinstance(event, TakePill):
            return Prozac()
        return self

class Grumpy:
    def run(self) -> None:
        print("What do you want?")
    def next(self, event: object) -> State:
        if isinstance(event, Calm):
            return Happy()
        if isinstance(event, TakePill):
            return Prozac()
        return self

class Prozac:
    def run(self) -> None:
        print("Everything is wonderful.")
    def next(self, event: object) -> State:
        return self

StateMachine(Happy()).run_all(
    [Annoy(), Calm(), TakePill(), Annoy()])
#: Great to see you!
#: Annoy
#: What do you want?
#: Calm
#: Great to see you!
#: TakePill
#: Everything is wonderful.
#: Annoy
#: Everything is wonderful.
