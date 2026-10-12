# state_machine.py
from collections.abc import Iterable
from state import State

class StateMachine:
    def __init__(self, initial_state: State) -> None:
        self.current_state = initial_state
        self.current_state.run()
    # Template method:
    def run_all(self, inputs: Iterable[object]) -> None:
        for input_ in inputs:
            state = self.current_state
            print(type(state).__name__, input_)
            self.current_state = state.next(input_)
            self.current_state.run()
