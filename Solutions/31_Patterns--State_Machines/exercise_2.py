# exercise_2.py
from collections.abc import Iterable
from typing import Protocol

# The chapter's state.py and state_machine.py, inlined:
class State(Protocol):
    def run(self) -> None: ...
    def next(self, input_: object) -> State: ...

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    def run_all(self, inputs: Iterable[object]) -> None:
        for input_ in inputs:
            state = self.current_state
            self.current_state = state.next(input_)
            print(type(state).__name__, input_, "->",
                  type(self.current_state).__name__)
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
    def next(self, input_: object) -> State:
        if isinstance(input_, Annoy):
            return Grumpy()
        if isinstance(input_, TakePill):
            return Prozac()
        return self

class Grumpy:
    def run(self) -> None:
        print("What do you want?")
    def next(self, input_: object) -> State:
        if isinstance(input_, Calm):
            return Happy()
        if isinstance(input_, TakePill):
            return Prozac()
        return self

class Prozac:
    def run(self) -> None:
        print("Everything is wonderful.")
    def next(self, input_: object) -> State:
        return self

StateMachine(Happy()).run_all(
    [Annoy(), Calm(), TakePill(), Annoy()])
#: Great to see you!
#: Happy Annoy -> Grumpy
#: What do you want?
#: Grumpy Calm -> Happy
#: Great to see you!
#: Happy TakePill -> Prozac
#: Everything is wonderful.
#: Prozac Annoy -> Prozac
#: Everything is wonderful.
